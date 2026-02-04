from __future__ import annotations

from langchain.tools import tool

from backend.models.interpolation import InterpolationResponse
from backend.utils.newton_interpolation_util import (
    backward_binomial_coefficient,
    compute_difference_table,
    select_optimal_x0_index,
    validate_equidistant,
    get_newton_backward_coefficients,
)


@tool
def newton_backward_interpolation(
    points: list[tuple[float, float]], x_eval: float
) -> dict:
    """
    Perform Newton backward difference interpolation.

    Given n+1 equidistantly spaced data points (x_i, y_i), computes the
    interpolating polynomial using Newton's backward difference formula:

        P_n(x) = f₀ + (s⁺,1)Δf₀ + (s⁺,2)Δ²f₀ + ... + (s⁺,n)Δⁿf₀

    where:
        s = (x - x₀) / h  is the interpolation variable
        h = x_{i+1} - x_i  is the constant step size
        (s⁺,k) = s(s+1)(s+2)...(s+k-1) / k!  is the backward binomial coeff
        Δᵏf₀  represents differences ending at position x₀

    This formula corresponds to equations (4.33) and (4.34) from the
    reference textbook. It is most accurate when interpolating near the
    END of the data set.

    The key difference from forward interpolation is:
    - Forward uses: (s,k) = s(s-1)(s-2)...(s-k+1) / k!
    - Backward uses: (s⁺,k) = s(s+1)(s+2)...(s+k-1) / k!

    And the differences are accessed from a different diagonal of the
    difference table (ending at x₀ rather than starting from x₀).

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
            - 'x0': The reference point x₀ used for interpolation
            - 'x0_index': Index of x₀ in the points array
            - 'polynomial_degree': Degree of the interpolating polynomial

    Raises:
        ValueError: If fewer than 2 points provided.
        ValueError: If duplicate x-coordinates exist.
        ValueError: If points are not equidistant.

    Example:
        >>> points = [(3.4, 0.294118), (3.5, 0.285714), (3.6, 0.277778)]
        >>> newton_backward_interpolation(points, 3.44)
        {
            'result': 0.290695,
            'coefficients': [a0, a1, a2],
            'polynomial_degree': 2
        }
    """
    # Validate minimum points
    if len(points) < 2:
        raise ValueError(
            "At least 2 points required for Newton backward interpolation."
        )

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

    # Select optimal starting index x₀ for backward interpolation
    x0_index = select_optimal_x0_index(x_values, x_eval, method="backward")
    x0 = x_values[x0_index]

    # Compute the interpolation variable s = (x_eval - x₀) / h
    # For backward interpolation, s is typically negative when
    # interpolating before x₀
    s = (x_eval - x0) / h

    # Build the forward difference table (same structure, different usage)
    difference_table = compute_difference_table(y_values)

    # Evaluate the Newton backward polynomial:
    # P(x) = f₀ + Σ (s⁺,k) * Δᵏf_{x0_index - k} for k=1 to x0_index
    #
    # The key insight: for backward interpolation, we use differences
    # that END at x₀, which means we need Δᵏf_{x0_index - k}
    result = difference_table[0][x0_index]  # Start with f₀

    # Add each term: (s⁺,k) * Δᵏf_{x0_index - k}
    max_k = min(x0_index + 1, len(difference_table))

    for k in range(1, max_k):
        # Access the difference that ends at x₀
        # For level k, we need the difference at index (x0_index - k)
        diff_index = x0_index - k

        if diff_index < 0 or diff_index >= len(difference_table[k]):
            break

        binomial = backward_binomial_coefficient(s, k)
        difference = difference_table[k][diff_index]
        result += binomial * difference

    # Calculate polynomial degree
    polynomial_degree = len(points) - 1

    coefficients = get_newton_backward_coefficients(y_values, x_values, x0_index, h)

    # Return structured response as dictionary
    return InterpolationResponse(
        result=result,
        coefficients=coefficients,
        polynomial_degree=polynomial_degree,
    ).model_dump()
