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


def get_polynomial_string(coefficients: list[float], precision: int = 2) -> str:
    """Constructs a LaTeX-formatted string representing a polynomial.

    Iterates through coefficients to build a string suitable for Matplotlib
    labels, handling signs, powers of x, and constant terms according to
    standard mathematical notation.

    Args:
        coefficients: A list of floats [a_0, a_1, ... a_n] where P(x) = a_0 + a_1*x...
        precision: The number of decimal places to show for each coefficient.
            Defaults to 2.

    Returns:
        A string formatted in LaTeX math mode.
        Example: "$P(x) = 1.00 - 2.50x + 0.12x^{2}$"

    Example:
        >>> get_polynomial_string([1.0, -2.5, 0.123])
        '$P(x) = 1.00 - 2.50x + 0.12x^{2}$'
    """
    if not coefficients:
        return "$P(x) = 0$"

    terms = []
    for i, coeff in enumerate(coefficients):
        # Skip zero coefficients unless it's the only term
        if coeff == 0 and len(coefficients) > 1:
            continue

        abs_val = abs(coeff)
        fmt_val = f"{abs_val:.{precision}f}"

        if i == 0:
            # First term (constant) - we keep the sign as is
            term = f"{coeff:.{precision}f}"
        else:
            # Handle sign with spacing
            sign = " + " if coeff >= 0 else " - "
            # Handle x, x^1, x^n logic
            if i == 1:
                x_part = "x"
            else:
                x_part = f"x^{{{i}}}"
            term = f"{sign}{fmt_val}{x_part}"

        terms.append(term)

    return f"$P(x) = {''.join(terms)}$"
