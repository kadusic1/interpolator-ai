from __future__ import annotations

from backend.models.interpolation import InterpolationResponse
from backend.utils.lagrange_interpolation_util import get_lagrange_coefficients
from backend.utils.general_util import evaluate_polynomial


def lagrange_interpolation(points: list[tuple[float, float]], x_eval: float) -> dict:
    """
    Perform Lagrange polynomial interpolation.

    Given n+1 data points (x_i, y_i), finds the unique polynomial P_n(x) of
    degree n that passes through all points using Lagrange basis polynomials,
    then evaluates it at x_eval.

    The method uses the formula:
        P_n(x) = Σ L_k(x) * f(x_k)  for k=0 to n

    where the Lagrange basis polynomials are:
        L_k(x) = Π (x - x_i)/(x_k - x_i)  for i=0 to n, i≠k

    This is equivalent to equation (4.22) and (4.23) from the reference:
        P_n(x) = L_0(x)f(x_0) + L_1(x)f(x_1) + ... + L_n(x)f(x_n)

    Args:
        points: List of (x, y) coordinate tuples. Must have at least 2 points.
        x_eval: The x-coordinate at which to evaluate the polynomial.

    Returns:
        Dictionary containing:
            - 'result': The interpolated y-value at x_eval
            - 'coefficients': List of polynomial coefficients [a0, a1, a2, ...]
            - 'polynomial_degree': Degree of the interpolating polynomial

    Raises:
        ValueError: If fewer than 2 points provided.
        ValueError: If duplicate x-coordinates exist.

    Example:
        >>> points = [(3.40, 0.294118), (3.50, 0.285714), (3.35, 0.298507)]
        >>> lagrange_interpolation(points, 3.45)
        {
            'result': 0.289855,
            'coefficients': [a0, a1, a2],
            'polynomial_degree': 2
        }
    """
    # Validate minimum points
    if len(points) < 2:
        raise ValueError("At least 2 points required for polynomial interpolation.")

    # Extract x and y values from points
    x_values = [p[0] for p in points]
    # Check for duplicate x-coordinates
    if len(set(x_values)) != len(x_values):
        raise ValueError("Duplicate x-coordinates detected in input points.")

    # Get polynomial coefficients (calculates basis polynomials once)
    coefficients = get_lagrange_coefficients(points)
    # Evaluate the polynomial at x_eval using the coefficients
    result = evaluate_polynomial(coefficients, x_eval)

    # Calculate polynomial degree (n-1 for n points)
    polynomial_degree = len(points) - 1

    # Return structured response as dictionary
    return InterpolationResponse(
        result=result,
        coefficients=coefficients,
        polynomial_degree=polynomial_degree,
    ).model_dump()
