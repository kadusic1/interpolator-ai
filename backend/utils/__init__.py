"""
Purpose: Provides shared utility functions, helpers, and common logic.
This module contains code that is reusable across different parts of the backend to adhere to DRY principles.

Relations:
- Helper module used by `backend.agent`, `backend.tools`, and `backend.api` as needed.
"""

from .equation_solver import bjorck_pereyra
from .newton_interpolation_util import (
    backward_binomial_coefficient,
    compute_difference_table,
    forward_binomial_coefficient,
    select_optimal_x0_index,
    validate_equidistant,
)

__all__ = [
    "bjorck_pereyra",
    "validate_equidistant",
    "compute_difference_table",
    "forward_binomial_coefficient",
    "backward_binomial_coefficient",
    "select_optimal_x0_index",
]
