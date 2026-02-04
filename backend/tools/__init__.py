"""
Purpose: Implements the core functionality and mathematical operations.
These tools are designed to be called by the AI agent to perform specific tasks (e.g., interpolation).

Relations:
- Executed by `backend.agent`.
- May utilize `backend.utils` for helper functions and `backend.models` for structured I/O.
"""

from .direct_interpolation import direct_interpolation
from .lagrange_interpolation import lagrange_interpolation

__all__ = ["direct_interpolation", "lagrange_interpolation"]
