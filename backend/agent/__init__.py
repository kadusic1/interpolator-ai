"""
Purpose: Defines the LangGraph agent, state machine, and orchestration logic.
This module is the "brain" of the application, deciding which actions to take.

Relations:
- Uses `backend.tools` to execute specific tasks.
- Uses `backend.models` for defining agent state and data structures.
"""

from backend.agent.pipeline import process_request

__all__ = ["process_request"]
