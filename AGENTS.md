# AGENTS.md - AI Coding Agent Guidelines

This document provides guidelines for AI coding agents working in this repository.

## Project Overview

This is a full-stack agentic numerical interpolation application built with:

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + TypeScript | Chat UI & visualization |
| API | FastAPI | REST endpoints for agent communication |
| Backend | Python 3.11+ + LangGraph | AI agent orchestration & validation |

The AI agent delegates all mathematical operations to specialized tools and
never performs calculations directly.

---

## Build & Development Commands

### Backend Setup

```bash
# Install dependencies with uv
uv sync
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running the Application

```bash
# Start the API server (from project root)
uv run uvicorn backend.api.main:app --reload --port 8000

# Start the frontend (in separate terminal)
cd frontend && npm run dev
```

### Running Both Services (Development)

```bash
# Option 1: Use separate terminals
# Terminal 1 - Backend API
uv run uvicorn backend.api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```


### Running Both Services (Development)

```bash
# Option 1: Use separate terminals
# Terminal 1 - Backend API
uvicorn backend.api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev

# Option 2: Use a process manager like honcho/foreman with Procfile
```

---

## Code Style Guidelines

### General Rules

- Follow the 80 char rule
- ALWAYS follow the DRY principle
- Don't leave unecessary whitespaces

### Python Version & Type Hints

- Target Python 3.11+
- Use type hints for all function signatures
- Use `from __future__ import annotations` for forward references

```python
from __future__ import annotations

def interpolate(points: list[tuple[float, float]], x_evals: list[float] | None) -> dict:
    ...
```

### Import Organization

Imports should be organized in this order, separated by blank lines:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import json
from pathlib import Path
from typing import Any

# Third-party
import numpy as np
from langgraph.graph import StateGraph
from pydantic import BaseModel

# Local
from backend.src.lagrange_interpolation import lagrange_interpolation
from backend.utils.parsing import parse_function
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `interpolation_result` |
| Functions | snake_case | `calculate_coefficients()` |
| Classes | PascalCase | `InterpolationTool` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_ITERATIONS` |
| Private | Leading underscore | `_internal_helper()` |
| Type aliases | PascalCase | `PointList = list[tuple[float, float]]` |

### Class & Function Structure

```python
class InterpolationTool:
    """Tool for performing numerical interpolation.

    Attributes:
        method: The interpolation method to use.
        precision: Number of decimal places for results.
    """

    def __init__(self, method: str = "lagrange", precision: int = 6) -> None:
        self.method = method
        self.precision = precision

    def interpolate(self, points: list[tuple[float, float]], x_evals: list[float] | None) -> dict:
        """Interpolate to find y values at given x evaluations.

        Args:
            points: List of (x, y) coordinate tuples.
            x_evals: List of x values to interpolate at.

        Returns:
            Dictionary with results and coefficients.

        Raises:
            ValueError: If fewer than 2 points provided.
        """
        if len(points) < 2:
            raise ValueError("At least 2 points required for interpolation")
        ...
```

### Error Handling

- Use specific exception types, not bare `except:`
- Create custom exceptions for domain-specific errors
- Always include meaningful error messages

```python
# Custom exceptions in backend/exceptions.py
class InterpolationError(Exception):
    """Base exception for interpolation errors."""
    pass

class InsufficientPointsError(InterpolationError):
    """Raised when not enough points provided."""
    pass

# Usage
try:
    result = interpolate(points, x)
except InsufficientPointsError as e:
    logger.error(f"Interpolation failed: {e}")
    raise
```

### LangGraph Specific Patterns

```python
from typing import Annotated, Sequence, TypedDict
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    """State passed between nodes in the extraction graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    parsed_output: InterpolationRequestList | None
    clean_requests: list[InterpolationRequest]
    valid: bool
    final_response_text: str | None

def build_extraction_graph() -> StateGraph:
    """Constructs the extraction pipeline graph."""
    workflow = StateGraph(AgentState)
    workflow.add_node("parse_input", parse_input_node)
    workflow.add_node("review_input", review_input_node)
    workflow.set_entry_point("parse_input")
    workflow.add_edge("parse_input", "review_input")
    return workflow.compile()
```

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def newton_interpolation(points: list[tuple[float, float]], x_evals: list[float] | None) -> dict:
    """Perform Newton's divided difference interpolation.

    Args:
        points: Data points as (x, y) tuples. Must have at least 2 points.
        x_evals: List of x-coordinates to evaluate the interpolating polynomial at.

    Returns:
        Dictionary containing interpolated y-values ('results') and coefficients.

    Raises:
        ValueError: If points list has fewer than 2 elements.

    Example:
        >>> points = [(0, 1), (1, 2), (2, 5)]
        >>> newton_interpolation(points, [1.5])
        {'results': [3.25], 'coefficients': [...]}
    """
```

### File Organization

```
/
├── backend/
│   ├── api/           # FastAPI + LangServe routes
│   ├── agent/         # LangGraph agent definition
│   ├── src/           # Core interpolation math functions
│   ├── models/        # Pydantic models
│   ├── utils/         # Utility functions
│   └── tests/         # Unit and integration tests
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types/
├── pyproject.toml
└── AGENTS.md
```

---

## Key Constraints

1. **No direct math**: The AI agent must delegate all calculations to tools
2. **Tool-first approach**: Prefer creating reusable tools over inline logic
3. **Session-only memory**: No persistent storage of chat history
4. **Domain focus**: Reject non-interpolation requests gracefully
5. **Strict Validation**:
    - Duplicate X coordinates MUST trigger immediate cancellation with a specific message.
    - Newton methods (forward/backward) REQUIRE equidistant points; otherwise, trigger immediate cancellation.
6. **Request Grouping**:
    - Multiple evaluation points for the SAME dataset must be grouped into a single `InterpolationRequest` with a list of `x_evals`.
    - Do NOT split the same dataset into multiple requests just because there are multiple X values to check.
