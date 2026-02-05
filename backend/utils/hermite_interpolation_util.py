"""
Hermite interpolation utility functions.

This module provides the core computational routines for Hermite polynomial
interpolation, which matches both function values and derivatives.
"""

from __future__ import annotations


def get_hermite_coefficients(
    x_values: list[float], y_values: list[float], dy_values: list[float]
) -> list[float]:
    """
    Compute polynomial coefficients for Hermite interpolation.

    Uses divided differences with repeated nodes to construct the Hermite
    polynomial that interpolates both function values and derivatives.

    The algorithm:
    1. Create a sequence z where each x_i appears twice
    2. Build divided difference table where:
       - f[z_2i, z_2i] = y_i (function value)
       - f[z_2i, z_2i+1] = y'_i (derivative value)
       - Higher order differences use standard divided difference formula
    3. Convert from nested form to standard polynomial form

    Args:
        x_values: List of n+1 distinct x-coordinates
        y_values: List of n+1 function values at x_values
        dy_values: List of n+1 derivative values at x_values

    Returns:
        List of polynomial coefficients [a0, a1, a2, ..., a_{2n+1}] in
        ascending power order, representing:
            P(x) = a0 + a1*x + a2*x^2 + ... + a_{2n+1}*x^{2n+1}
    """
    n = len(x_values)

    # Create doubled node sequence: [x0, x0, x1, x1, ..., xn, xn]
    z = []
    for x in x_values:
        z.append(x)
        z.append(x)

    # Build divided difference table
    # Q[i][j] represents f[z_i, z_{i+1}, ..., z_{i+j}]
    size = 2 * n
    Q = [[0.0] * size for _ in range(size)]

    # Fill first column with function values
    for i in range(n):
        Q[2 * i][0] = y_values[i]
        Q[2 * i + 1][0] = y_values[i]

    # Fill second column with derivatives and first-order differences
    for i in range(n):
        Q[2 * i][1] = dy_values[i]
        if i < n - 1:
            # First order divided difference between distinct points
            Q[2 * i + 1][1] = (Q[2 * i + 2][0] - Q[2 * i + 1][0]) / (
                z[2 * i + 2] - z[2 * i + 1]
            )

    # Fill remaining columns using divided difference formula
    for j in range(2, size):
        for i in range(size - j):
            if abs(z[i + j] - z[i]) < 1e-15:
                # This shouldn't happen with our setup, but handle gracefully
                Q[i][j] = 0.0
            else:
                Q[i][j] = (Q[i + 1][j - 1] - Q[i][j - 1]) / (z[i + j] - z[i])

    # The divided differences along the top diagonal are the coefficients
    # for the nested form: H(x) = Q[0][0] + Q[0][1]*(x-z0) + Q[0][2]*(x-z0)*(x-z1) + ...
    nested_coeffs = [Q[0][j] for j in range(size)]

    # Convert from nested form to standard polynomial form
    coefficients = convert_nested_to_standard(nested_coeffs, z)

    return coefficients


def convert_nested_to_standard(
    nested_coeffs: list[float], nodes: list[float]
) -> list[float]:
    """
    Convert nested (Newton) form to standard polynomial form.

    Nested form:
        P(x) = c0 + c1*(x-z0) + c2*(x-z0)*(x-z1) + ... + cn*(x-z0)*...*(x-z_{n-1})

    Standard form:
        P(x) = a0 + a1*x + a2*x^2 + ... + an*x^n

    Algorithm:
        Start with the highest degree term and work backwards, expanding
        each (x - z_i) factor and accumulating coefficients.

    Args:
        nested_coeffs: Coefficients [c0, c1, ..., cn] from nested form
        nodes: Node sequence [z0, z1, ..., z_{n-1}]

    Returns:
        Coefficients [a0, a1, ..., an] in standard form
    """
    n = len(nested_coeffs)

    # Initialize with the last (highest degree) term
    # Start with: cn
    poly = [nested_coeffs[-1]]

    # Work backwards, multiplying by (x - z_i) and adding next coefficient
    for i in range(n - 2, -1, -1):
        # Multiply current polynomial by (x - nodes[i])
        # (x - z_i) * P(x) = x*P(x) - z_i*P(x)
        new_poly = [0.0] * (len(poly) + 1)

        # x * P(x) contributes to higher degree terms
        for j in range(len(poly)):
            new_poly[j + 1] += poly[j]

        # -z_i * P(x) contributes to same degree terms
        for j in range(len(poly)):
            new_poly[j] -= nodes[i] * poly[j]

        # Add the next nested coefficient to the constant term
        new_poly[0] += nested_coeffs[i]

        poly = new_poly

    return poly
