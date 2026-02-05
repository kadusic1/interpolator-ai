from __future__ import annotations
import numpy as np
from backend.models.interpolation import InterpolationResponse
from backend.utils.general_util import evaluate_polynomial
from backend.utils.hermite_interpolation_util import get_hermite_coefficients


def hermite_interpolation(
    points: list[tuple[float, float]], x_evals: list[float] | None
) -> dict:
    """
    Perform Hermite polynomial interpolation.

    Given n+1 data points (x_i, y_i), finds the unique polynomial
    H_{2n+1}(x) of degree at most 2n+1 that passes through all points and
    matches the derivatives estimated from the data.

    The Hermite polynomial satisfies:
        H(x_i) = y_i        for i = 0, 1, ..., n
        H'(x_i) = y'_i      for i = 0, 1, ..., n

    where y'_i are estimated using numpy.gradient, which computes accurate
    second-order central differences for interior points and second-order
    one-sided differences at the boundaries.

    This is constructed using the divided difference formula:
        H(x) = Σ c_k * w_k(x)

    where w_k(x) are the nested products:
        w_0(x) = 1
        w_1(x) = (x - z_0)
        w_2(x) = (x - z_0)(x - z_1)
        ...

    and z_0, z_1, ..., z_{2n+1} is the sequence where each x_i appears twice
    (once for the function value, once for the derivative).

    The coefficients c_k are computed using divided differences with
    derivative information included.

    Args:
        points: List of (x, y) coordinate tuples. Must have at least 2 points.
        x_evals: List of x-coordinates at which to evaluate the polynomial.

    Returns:
        Dictionary containing:
            - 'results': The interpolated y-values at x_evals
            - 'coefficients': List of polynomial coefficients [a0, a1, a2, ...]
              in ascending power order
            - 'polynomial_degree': Degree of the interpolating polynomial

    Raises:
        ValueError: If fewer than 2 points provided.
        ValueError: If duplicate x-coordinates exist.

    Example:
        >>> points = [(1.0, 2.0), (2.0, 5.0), (3.0, 4.0)]
        >>> hermite_interpolation(points, [1.5])
        {
            'results': [3.125],
            'coefficients': [a0, a1, a2, a3, a4, a5],
            'polynomial_degree': 5
        }

    Note:
        For n+1 data points, the resulting polynomial has degree at most 2n+1,
        giving 2n+2 coefficients. Derivatives are automatically estimated using
        numpy.gradient for smooth interpolation.
    """
    # Validate minimum points
    if len(points) < 2:
        raise ValueError("At least 2 points required for Hermite interpolation.")

    # Extract x and y values
    x_values = [p[0] for p in points]
    y_values = [p[1] for p in points]

    # Check for duplicate x-coordinates
    if len(set(x_values)) != len(x_values):
        raise ValueError("Duplicate x-coordinates detected in input points.")

    # Sort points by x-coordinate for proper derivative estimation
    sorted_indices = sorted(range(len(x_values)), key=lambda i: x_values[i])
    x_values = [x_values[i] for i in sorted_indices]
    y_values = [y_values[i] for i in sorted_indices]

    # Use numpy.gradient to estimate derivatives
    # numpy.gradient computes dy/dx where spacing between points varies
    x_array = np.array(x_values)
    y_array = np.array(y_values)
    dy_array = np.gradient(y_array, x_array)
    dy_values = dy_array.tolist()

    # Get polynomial coefficients using Hermite divided differences
    coefficients = get_hermite_coefficients(x_values, y_values, dy_values)

    # Evaluate the polynomial at x_evals using the coefficients
    results = None
    if x_evals:
        results = [evaluate_polynomial(coefficients, x) for x in x_evals]

    # Calculate polynomial degree (2n+1 for n+1 points)
    polynomial_degree = 2 * len(points) - 1

    # Return structured response as dictionary
    return InterpolationResponse(
        results=results,
        coefficients=coefficients,
        polynomial_degree=polynomial_degree,
    ).model_dump()
