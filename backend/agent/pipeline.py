from __future__ import annotations

import logging
import operator
import sys
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from backend.agent.prompts import REVIEW_ERROR_TEMPLATE, SYSTEM_PROMPT
from backend.models.interpolation import (
    InterpolationRequest,
    InterpolationRequestList,
    InterpolationResponseWithMetadata,
)
from backend.src.direct_interpolation import direct_interpolation
from backend.src.graph_polynomial import graph_polynomial
from backend.src.lagrange_interpolation import lagrange_interpolation
from backend.src.newton_backward_interpolation import newton_backward_interpolation
from backend.src.newton_forward_interpolation import newton_forward_interpolation
from backend.src.hermite_interpolation import hermite_interpolation

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# --- State Definition ---
class AgentState(TypedDict):
    """
    State passed between nodes in the extraction graph.

    Attributes:
        messages: The conversation history.
        parsed_output: The raw structured output from the LLM parser.
        clean_requests: The list of validated interpolation requests.
        valid: Boolean flag indicating if the requests are valid and ready for execution.
        final_response_text: Text response for non-interpolation queries.
        method: The interpolation method to use ("lagrange", "newton_forward",
        "newton_backward", "direct", "hermite").
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]
    parsed_output: InterpolationRequestList | None
    clean_requests: list[InterpolationRequest]
    valid: bool
    final_response_text: str | None
    method: str | None


# --- Nodes ---


def parse_input_node(state: AgentState) -> dict:
    """
    Invokes the LLM to parse natural language into structured interpolation requests.

    It ensures the system prompt is present in the context and uses the structured
    output capability of the LLM.

    Args:
        state: The current agent state containing conversation history.

    Returns:
        A dictionary update for the state containing the 'parsed_output'.
    """
    messages = state["messages"]

    # Ensure System Prompt is the first message for the LLM context
    # We construct a transient list if needed, to avoid duplicating it in state history
    if not any(isinstance(m, SystemMessage) for m in messages):
        llm_messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    else:
        llm_messages = messages

    # Use Vision-capable model for multimodal support
    llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0)
    structured_llm = llm.with_structured_output(InterpolationRequestList)

    try:
        response = structured_llm.invoke(llm_messages)
        return {"parsed_output": response}
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        # Return None to trigger the review node's error handling (which forces a retry)
        # instead of exiting immediately.
        return {"parsed_output": None}


def review_input_node(state: AgentState) -> dict:
    """
    Deterministically validates the extracted requests.

    Checks for:
    1.  Minimum number of points (>= 2).
    2.  Unique x-coordinates.

    If errors are found, it constructs a feedback message using `REVIEW_ERROR_TEMPLATE`
    to prompt the LLM to retry.

    Args:
        state: The current agent state containing 'parsed_output'.

    Returns:
        A dictionary update for the state:
        - If valid: {'valid': True, 'clean_requests': [...]}
        - If invalid: {'valid': False, 'messages': [HumanMessage(...)]}
        - If not interpolation: {'valid': True, 'final_response_text': ...}
    """
    output = state["parsed_output"]

    # 1. Handle missing output or non-interpolation requests
    if not output:
        return {
            "valid": False,
            "messages": [
                HumanMessage(content="System Error: No output received from parser.")
            ],
        }

    if not output.is_interpolation_request:
        return {
            "valid": True,
            "clean_requests": [],
            "final_response_text": output.clarification_message
            or "Ja sam interpolacijski agent. Unesite problem relevantan za interpolaciju.",
        }

    # 2. Validate Requests
    valid_requests = []
    errors = []
    method = state.get("method")

    for _, req in enumerate(output.requests):
        # Check points count
        if len(req.points) < 2:
            return {
                "valid": True,
                "clean_requests": [],
                "final_response_text": f"Morate imati najmanje 2 jedinstvene x-koordinate za interpolaciju.",
            }

        # Check unique x - STRICT CANCELLATION
        x_vals = [p[0] for p in req.points]
        if len(set(x_vals)) != len(x_vals):
            return {
                "valid": True,
                "clean_requests": [],
                "final_response_text": "Duplikati x-koordinata nisu dozvoljeni.",
            }

        # Check equidistant for Newton methods - STRICT CANCELLATION
        if method in ("newton_forward", "newton_backward"):
            x_sorted = sorted(x_vals)
            diffs = [x_sorted[i + 1] - x_sorted[i] for i in range(len(x_sorted) - 1)]
            # Check if any difference deviates from the first one significantly
            if diffs and not all(abs(d - diffs[0]) < 1e-9 for d in diffs):
                return {
                    "valid": True,
                    "clean_requests": [],
                    "final_response_text": f"Za Newtonove metode, x-koordinate moraju biti jednako udaljene (ekvidistantne).",
                }

        valid_requests.append(req)

    # 3. Return Result
    if errors:
        feedback_msg = REVIEW_ERROR_TEMPLATE.format(errors="; ".join(errors))
        return {"valid": False, "messages": [HumanMessage(content=feedback_msg)]}

    return {"valid": True, "clean_requests": valid_requests}


# --- Graph Construction ---


def build_extraction_graph():
    """
    Constructs the LangGraph state graph for the extraction pipeline.

    Returns:
        Compiled StateGraph.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_input", parse_input_node)
    workflow.add_node("review_input", review_input_node)

    workflow.set_entry_point("parse_input")
    workflow.add_edge("parse_input", "review_input")

    def router(state: AgentState):
        return END if state["valid"] else "parse_input"

    workflow.add_conditional_edges("review_input", router)

    return workflow.compile()


# --- Main Pipeline Execution ---


def process_request(
    user_input: str, image_base64: str | None = None, method: str = "lagrange"
) -> list[InterpolationResponseWithMetadata] | str:
    """
    Orchestrates the full interpolation pipeline.

    Workflow:
    1.  **Extraction**: Runs the LangGraph (parse -> review loop) to get structured data.
    2.  **Execution**: Iterates through valid requests and calls the appropriate
        math function from `backend/src`.
    3.  **Graphing**: Generates plots for each result using `graph_polynomial`.
    4.  **Response**: Aggregates results into `InterpolationResponseWithMetadata` objects.

    Args:
        user_input: The raw natural language string from the user.
        image_base64: Optional base64 encoded image string (without data URI prefix).

    Returns:
        A list of `InterpolationResponseWithMetadata` objects containing results and graphs,
        OR a string message if the request was unrelated to interpolation.
    """
    graph = build_extraction_graph()

    # Construct content payload
    if image_base64:
        # Multimodal message structure
        content = [
            {"type": "text", "text": user_input},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            },
        ]
    else:
        # Text-only message
        content = user_input

    initial_state = {
        "messages": [HumanMessage(content=content)],
        "parsed_output": None,
        "clean_requests": [],
        "valid": False,
        "final_response_text": None,
        "method": method,
    }

    # Run Extraction Graph
    try:
        final_state = graph.invoke(initial_state, config={"recursion_limit": 12})
        # Calculate steps based on history: (User Msg + Error Msgs) * 2 nodes per pass
        steps = len(final_state["messages"]) * 2
        # Log both the logic loops and the engine steps
        logger.info(
            f"Graph finished. Loops: {(len(final_state['messages']) + 1) // 2} | Recursion Steps: {steps}"
        )
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return "Invalid interpolation request. Please ensure your input is clear and try again."

    # Handle Non-Interpolation / Clarification
    if final_state.get("final_response_text"):
        return final_state["final_response_text"]

    requests = final_state.get("clean_requests", [])
    if not requests:
        return "No valid interpolation requests found."

    results = []

    # Deterministic Execution Loop
    for req in requests:
        try:
            # Route to appropriate math function
            if method == "lagrange":
                response_dict = lagrange_interpolation(req.points, req.x_evals)
            elif method == "newton_forward":
                response_dict = newton_forward_interpolation(req.points, req.x_evals)
            elif method == "newton_backward":
                response_dict = newton_backward_interpolation(req.points, req.x_evals)
            elif method == "direct":
                response_dict = direct_interpolation(req.points, req.x_evals)
            elif method == "hermite":
                response_dict = hermite_interpolation(req.points, req.x_evals)
            else:
                response_dict = lagrange_interpolation(req.points, req.x_evals)

            # Generate Graph
            coeffs = response_dict["coefficients"]
            graph_result = graph_polynomial(coeffs, req.points)

            # Map raw y-values to (x, y) tuples if evaluation points exist
            raw_results = response_dict.get("results")
            formatted_results = None
            if raw_results and req.x_evals:
                formatted_results = list(zip(req.x_evals, raw_results))

            # Aggregate Result
            final_obj = InterpolationResponseWithMetadata(
                **response_dict,
                points=req.points,
                method=method,
                image_base64=graph_result["image_base64"],
                formatted_results=formatted_results,
            )
            results.append(final_obj)

        except Exception as e:
            logger.error(f"Error processing request {req}: {e}")
            continue

    return results
