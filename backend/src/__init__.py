"""
Purpose: Implements the core functionality and mathematical operations.
These tools are designed to be called by the AI agent to perform specific tasks (e.g., interpolation).

Relations:
- Executed by `backend.agent`.
- May utilize `backend.utils` for helper functions and `backend.models` for structured I/O.
"""

from .direct_interpolation import direct_interpolation
from .graph_polynomial import graph_polynomial
from .lagrange_interpolation import lagrange_interpolation
from .newton_backward_interpolation import newton_backward_interpolation
from .newton_forward_interpolation import newton_forward_interpolation
from .hermite_interpolation import hermite_interpolation

__all__ = [
    "direct_interpolation",
    "graph_polynomial",
    "lagrange_interpolation",
    "newton_forward_interpolation",
    "newton_backward_interpolation",
    "hermite_interpolation",
]
