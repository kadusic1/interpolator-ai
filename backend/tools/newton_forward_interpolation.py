from __future__ import annotations

from langchain.tools import tool

from backend.models.interpolation import InterpolationResponse
from backend.utils.newton_interpolation_util import (
    compute_difference_table,
    forward_binomial_coefficient,
    get_newton_forward_coefficients,
    select_optimal_x0_index,
    validate_equidistant,
)


@tool
def newton_forward_interpolation(
    points: list[tuple[float, float]], x_eval: float
) -> dict:
    """
    Perform Newton forward difference interpolation.

    Given n+1 equidistantly spaced data points (x_i, y_i), computes the
    interpolating polynomial using Newton's forward difference formula:

        P_n(x) = f₀ + (s,1)Δf₀ + (s,2)Δ²f₀ + ... + (s,n)Δⁿf₀

    where:
        s = (x - x₀) / h  is the interpolation variable
        h = x_{i+1} - x_i  is the constant step size
        (s,k) = s(s-1)(s-2)...(s-k+1) / k!  is the forward binomial coeff
        Δᵏf₀  is the k-th forward difference at position x₀

    This formula corresponds to equations (4.27) and (4.28) from the
    reference textbook. It is most accurate when interpolating near the
    BEGINNING of the data set.

    The forward differences are computed using:
        Δf_j = f_{j+1} - f_j
        Δ²f_j = Δf_{j+1} - Δf_j
        ...

    Args:
        points: Equidistantly spaced (x, y) tuples. Must have at least
            2 points.
        x_eval: The x-coordinate at which to evaluate the polynomial.

    Returns:
        Dictionary containing:
            - 'result': The interpolated y-value at x_eval
            - 'difference_table': Full triangular table of forward
              differences [[f_0, f_1, ...], [Δf_0, Δf_1, ...], ...]
            - 'step_size': The constant step h
            - 's_parameter': The value of s = (x_eval - x₀) / h
            - 'x0': The starting point x₀ used for interpolation
            - 'x0_index': Index of x₀ in the points array
            - 'polynomial_degree': Degree of the interpolating polynomial

    Raises:
        ValueError: If fewer than 2 points provided.
        ValueError: If duplicate x-coordinates exist.
        ValueError: If points are not equidistant.

    Example:
        >>> points = [(3.4, 0.294118), (3.5, 0.285714), (3.6, 0.277778)]
        >>> newton_forward_interpolation(points, 3.44)
        {
            'result': 0.290756,
            'coefficients': [a0, a1, a2],
            'polynomial_degree': 2
        }
    """
    # Validate minimum points
    if len(points) < 2:
        raise ValueError("At least 2 points required for Newton forward interpolation.")

    # Sort points by x-coordinate
    sorted_points = sorted(points, key=lambda p: p[0])

    # Extract x and y values
    x_values = [p[0] for p in sorted_points]
    y_values = [p[1] for p in sorted_points]

    # Check for duplicate x-coordinates
    if len(set(x_values)) != len(x_values):
        raise ValueError("Duplicate x-coordinates detected in input points.")

    # Validate equidistant spacing and get step size h
    h = validate_equidistant(x_values)

    # Select optimal starting index x₀ for forward interpolation
    x0_index = select_optimal_x0_index(x_values, x_eval, method="forward")
    x0 = x_values[x0_index]

    # Compute the interpolation variable s = (x_eval - x₀) / h
    s = (x_eval - x0) / h

    # Build the forward difference table
    difference_table = compute_difference_table(y_values)

    # Evaluate the Newton forward polynomial:
    # P(x) = f₀ + Σ (s,k) * Δᵏf₀ for k=1 to n
    result = difference_table[0][x0_index]  # Start with f₀

    # Add each term: (s,k) * Δᵏf_{x0_index}
    n = len(points)
    for k in range(1, n - x0_index):
        # Check if we have enough differences at this level
        if k >= len(difference_table) or x0_index >= len(difference_table[k]):
            break

        binomial = forward_binomial_coefficient(s, k)
        difference = difference_table[k][x0_index]
        result += binomial * difference

    coefficients = get_newton_forward_coefficients(y_values, x_values, x0_index, h)

    # Calculate polynomial degree
    polynomial_degree = len(points) - 1

    # Return structured response as dictionary
    return InterpolationResponse(
        result=result,
        coefficients=coefficients,
        polynomial_degree=polynomial_degree,
    ).model_dump()
