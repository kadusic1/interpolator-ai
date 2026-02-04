"""
Purpose: Implements the core functionality and mathematical operations.
These tools are designed to be called by the AI agent to perform specific tasks (e.g., interpolation).

Relations:
- Executed by `backend.agent`.
- May utilize `backend.utils` for helper functions and `backend.models` for structured I/O.
"""

from .equation_solver import bjorck_pereyra
from .direct_interpolation import direct_interpolation

__all__ = ["bjorck_pereyra", "direct_interpolation"]
