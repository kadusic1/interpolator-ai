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
from .general_util import multiply_polynomials, evaluate_polynomial
from .lagrange_interpolation_util import get_lagrange_coefficients
from .hermite_interpolation_util import get_hermite_coefficients

__all__ = [
    "bjorck_pereyra",
    "validate_equidistant",
    "compute_difference_table",
    "forward_binomial_coefficient",
    "backward_binomial_coefficient",
    "select_optimal_x0_index",
    "multiply_polynomials",
    "get_lagrange_coefficients",
    "evaluate_polynomial",
    "get_hermite_coefficients",
]
