from __future__ import annotations

from backend.models.interpolation import InterpolationResponse
from backend.utils.equation_solver import bjorck_pereyra


def direct_interpolation(
    points: list[tuple[float, float]], x_evals: list[float] | None
) -> dict:
    """
    Perform direct polynomial interpolation using Vandermonde system.

    Given n+1 data points (x_i, y_i), finds the unique polynomial P_n(x) of
    degree n that passes through all points, then evaluates it at x_eval.

    The method constructs the Vandermonde system:
        y_0 = a_0 + a_1*x_0 + a_2*x_0^2 + ... + a_n*x_0^n
        y_1 = a_0 + a_1*x_1 + a_2*x_1^2 + ... + a_n*x_1^n
        ...
        y_n = a_0 + a_1*x_n + a_2*x_n^2 + ... + a_n*x_n^n

    And solves it using the Bjorck-Pereyra algorithm for O(n^2) efficiency.

    Args:
        points: List of (x, y) coordinate tuples. Must have at least 2 points.
        x_evals: List of x-coordinates at which to evaluate the polynomial.

    Returns:
        Dictionary containing:
            - 'results': The interpolated y-values at x_evals
            - 'coefficients': Polynomial coefficients [a_0, a_1, ...] in
              ascending power order
            - 'polynomial_degree': Degree of the interpolating polynomial

    Raises:
        ValueError: If fewer than 2 points provided.
        ValueError: If duplicate x-coordinates exist.

    Example:
        >>> points = [(0.0, 1.0), (1.0, 2.0), (2.0, 5.0)]
        >>> direct_interpolation(points, [1.5])
        {
            'results': [3.25],
            'coefficients': [1.0, 0.0, 1.0],
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
    y_values = [p[1] for p in points]

    # Solve Vandermonde system using Bjorck-Pereyra algorithm
    # This returns coefficients [a_0, a_1, ..., a_n] in ascending power order
    coefficients = bjorck_pereyra(x_values, y_values)

    # Evaluate polynomial at x_evals using Horner's method
    results = None
    if x_evals:
        results = []
        for x in x_evals:
            res = 0.0
            for coef in reversed(coefficients):
                res = res * x + coef
            results.append(res)

    # Calculate polynomial degree (n for n+1 points)
    polynomial_degree = len(points) - 1

    # Return structured response as dictionary
    return InterpolationResponse(
        results=results,
        coefficients=coefficients,
        polynomial_degree=polynomial_degree,
    ).model_dump()
