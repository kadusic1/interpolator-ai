# AGENTS.md - AI Coding Agent Guidelines

This document provides guidelines for AI coding agents working in this repository.

## Project Overview

This is a full-stack agentic numerical interpolation application built with:

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + TypeScript | Chat UI & visualization |
| API | FastAPI + LangServe | REST endpoints & agent serving |
| Backend | Python 3.11+ + LangGraph | AI agent orchestration |

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
uvicorn backend.api.main:app --reload --port 8000

# Start the frontend (in separate terminal)
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

def interpolate(points: list[tuple[float, float]], x: float) -> float:
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
from backend.tools.interpolation import lagrange_interpolate
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

    def interpolate(self, points: list[tuple[float, float]], x: float) -> float:
        """Interpolate to find y value at given x.

        Args:
            points: List of (x, y) coordinate tuples.
            x: The x value to interpolate at.

        Returns:
            The interpolated y value.

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
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    """State passed between graph nodes."""
    messages: list[dict[str, Any]]
    points: list[tuple[float, float]] | None
    result: float | None

def create_graph() -> StateGraph:
    """Create the interpolation agent graph."""
    graph = StateGraph(AgentState)
    graph.add_node("parse_input", parse_input_node)
    graph.add_node("interpolate", interpolation_node)
    graph.add_edge("parse_input", "interpolate")
    graph.add_edge("interpolate", END)
    return graph.compile()
```

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def newton_interpolation(points: list[tuple[float, float]], x: float) -> float:
    """Perform Newton's divided difference interpolation.

    Args:
        points: Data points as (x, y) tuples. Must have at least 2 points.
        x: The x-coordinate to evaluate the interpolating polynomial at.

    Returns:
        The interpolated y-value at the given x coordinate.

    Raises:
        ValueError: If points list has fewer than 2 elements.

    Example:
        >>> points = [(0, 1), (1, 2), (2, 5)]
        >>> newton_interpolation(points, 1.5)
        3.25
    """
```

### File Organization

```
/
├── backend/
│   ├── api/           # FastAPI + LangServe routes
│   ├── agent/         # LangGraph agent definition
│   ├── tools/         # Tool implementations
│   ├── models/        # Pydantic models
│   └── utils/         # Utility functions
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
