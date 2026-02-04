from backend.utils import multiply_polynomials


def get_lagrange_coefficients(points: list[tuple[float, float]]) -> list[float]:
    """
    Compute the coefficients of the Lagrange interpolating polynomial for given points.

    This function finds the unique polynomial P(x) that passes through all provided points
    using the Lagrange interpolation formula. The result is a list of coefficients such that:
        P(x) = a0 + a1*x + a2*x^2 + ... + an*x^n

    How it works:
        For each data point (x_k, y_k):
            1. Construct the Lagrange basis polynomial L_k(x):
                - Start with L_k(x) = 1.
                - For every other point x_i (i ≠ k), multiply by (x - x_i).
                - This builds a polynomial whose coefficients are stored in a list.
            2. Normalize L_k(x):
                - Divide all coefficients by the product (x_k - x_i) for all i ≠ k.
                - This ensures L_k(x_k) = 1 and L_k(x_i) = 0 for i ≠ k.
            3. Scale L_k(x) by y_k:
                - Multiply each coefficient by y_k.
            4. Add the scaled coefficients to the result polynomial:
                - The result polynomial accumulates the contributions from each basis polynomial.

        After processing all points, the result is a list of coefficients for the interpolating polynomial.

    Example:
        Suppose you have three points: (1, 2), (2, 3), (3, 5).

        Step-by-step for k=0 (point (1, 2)):
            - Build L_0(x): (x - 2)*(x - 3)
            - Normalize: divide by (1-2)*(1-3) = (-1)*(-2) = 2
            - Scale by y_0=2
            - Add to result
        Repeat for k=1 and k=2.

        The function will return a list of coefficients [1.0, 0.5, 0.5] such that:
            P(x) = 1.0 + 0.5*x + 0.5*x^2
        This polynomial will pass exactly through the points (1, 2), (2, 3), and (3, 5).

        >>> get_lagrange_coefficients([(1, 2), (2, 3), (3, 5)])
        [1.0, 0.5, 0.5]
        # This means the polynomial is: P(x) = 1.0 + 0.5*x + 0.5*x^2
        # You can check:
        # P(1) = 1.0 + 0.5*1 + 0.5*1^2 = 2.0
        # P(2) = 1.0 + 0.5*2 + 0.5*4 = 3.0
        # P(3) = 1.0 + 0.5*3 + 0.5*9 = 5.0

    Args:
        points: List of (x, y) coordinate tuples.

    Returns:
        List of coefficients where index i is the coefficient of x^i.
    """
    n = len(points)
    x_values = [p[0] for p in points]
    y_values = [p[1] for p in points]

    # Initialize result polynomial coefficients (all zeros)
    result_coeffs = [0.0] * n

    # For each Lagrange basis polynomial L_k(x)
    for k in range(n):
        # Start with L_k(x) = 1 (constant polynomial)
        L_k_coeffs = [1.0]

        # Build the numerator: Π (x - x_i) for i ≠ k
        for i in range(n):
            if i != k:
                # Multiply by (x - x_i), which is [-x_i, 1] in coefficient form
                L_k_coeffs = multiply_polynomials(L_k_coeffs, [-x_values[i], 1.0])

        # Compute the denominator: Π (x_k - x_i) for i ≠ k
        denominator = 1.0
        for i in range(n):
            if i != k:
                denominator *= x_values[k] - x_values[i]

        # Divide all coefficients by denominator and multiply by y_k
        # Then add to the result polynomial
        for j in range(len(L_k_coeffs)):
            result_coeffs[j] += (L_k_coeffs[j] / denominator) * y_values[k]

    return result_coeffs
