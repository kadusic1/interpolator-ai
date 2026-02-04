def multiply_polynomials(p1: list[float], p2: list[float]) -> list[float]:
    """Multiply two polynomials represented as coefficient lists.
    Index i in the list corresponds to the coefficient for x^i.

    Args:
        p1: List of coefficients for the first polynomial.
        p2: List of coefficients for the second polynomial.

    Returns:
        A list of coefficients representing the product polynomial.

    Example:
        >>> multiply_polynomials([1, 2], [3, 4])
        [3.0, 10.0, 8.0]
    """
    result = [0.0] * (len(p1) + len(p2) - 1)
    for i, coeff1 in enumerate(p1):
        for j, coeff2 in enumerate(p2):
            result[i + j] += coeff1 * coeff2
    return result


def evaluate_polynomial(coeffs: list[float], x: float) -> float:
    """Evaluate a polynomial at a given value using Horner's method.

    Args:
        coeffs: List of coefficients where index i is the coefficient of x^i.
        x: The value at which to evaluate the polynomial.

    Returns:
        The evaluated result as a float.

    Example:
        >>> evaluate_polynomial([1, 2, 3], 2)
        17.0
    """
    result = 0.0
    for i in range(len(coeffs) - 1, -1, -1):
        result = result * x + coeffs[i]
    return result
