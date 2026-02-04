def bjorck_pereyra(
    x: list[float], f: list[float], tolerance: float = 1e-10
) -> list[float]:
    """
    Solve Vandermonde system Vc = f using Bjorck-Pereyra algorithm.

    Given nodes x_0, x_1, ..., x_{n-1} and values f_0, f_1, ..., f_{n-1},
    finds coefficients c_0, c_1, ..., c_{n-1} of the interpolating polynomial:
        p(x) = c_0 + c_1*x + c_2*x^2 + ... + c_{n-1}*x^{n-1}
    such that p(x_i) = f_i for all i.

    The Vandermonde matrix V has structure V[i][j] = x_i^j.
    This algorithm exploits divided difference structure to achieve O(n^2)
    complexity instead of O(n^3) for general LU decomposition.

    Args:
        x: List of n distinct interpolation nodes.
        f: List of n function values at the nodes.
        tolerance: Tolerance for detecting duplicate nodes (default: 1e-10).

    Returns:
        List of n polynomial coefficients [c_0, c_1, ..., c_{n-1}] in
        ascending power order (c_0 is constant term).

    Raises:
        ValueError: If x and f have different lengths.
        ValueError: If fewer than 1 point is provided.
        ValueError: If duplicate or near-duplicate nodes are detected.

    Example:
        >>> x = [0.0, 1.0, 2.0]
        >>> f = [1.0, 2.0, 5.0]
        >>> c = bjorck_pereyra(x, f)
    """
    # Copy inputs to avoid modifying originals
    x = x[:]
    c = f[:]

    # Number of nodes/equations
    n = len(x)

    # Validate input lengths match
    if len(f) != n:
        raise ValueError(
            f"ERROR: Length mismatch - len(x)={n}, len(f)={len(f)}.\n"
            f"Node list and value list must have same length."
        )

    # Check minimum size
    if n < 1:
        raise ValueError("ERROR: At least 1 data point required for interpolation.")

    # Check for duplicate nodes (O(n^2) but thorough)
    # Vandermonde matrix is singular if any two nodes are equal
    for i in range(n):
        for j in range(i + 1, n):
            if abs(x[i] - x[j]) < tolerance:
                raise ValueError(
                    f"ERROR: Duplicate nodes detected!\n"
                    f"x[{i}] = {x[i]}, x[{j}] = {x[j]}\n"
                    f"|x[{i}] - x[{j}]| = {abs(x[i] - x[j]):.2e} < "
                    f"tolerance {tolerance:.2e}"
                )

    # Handle trivial case - single point
    if n == 1:
        return c

    # Phase 1: Forward elimination (computing divided differences)
    for k in range(n - 1):
        # Process indices from n-1 down to k+1
        # This ensures c[i-1] is still the old value when we update c[i]
        for i in range(n - 1, k, -1):
            # Compute difference of nodes for division
            # x[i] and x[i-k-1] are separated by k+1 positions
            diff = x[i] - x[i - k - 1]

            # Check for near-zero denominator (would indicate duplicate nodes)
            if abs(diff) < tolerance:
                raise ValueError(
                    f"ERROR: Near-duplicate nodes detected in Phase 1!\n"
                    f"x[{i}] = {x[i]}, x[{i - k - 1}] = {x[i - k - 1]}\n"
                    f"difference = {diff:.2e} < tolerance {tolerance:.2e}"
                )

            # Divided difference formula
            # This computes f[x_{i-k-1}, ..., x_i] from lower-order differences
            c[i] = (c[i] - c[i - 1]) / diff

    # Phase 2: Backward substitution (Newton to monomial form)
    for k in range(n - 2, -1, -1):
        # Process indices from k to n-2
        # This accumulates contribution from higher-degree terms
        for i in range(k, n - 1):
            # Horner-like step: subtract contribution from next coefficient
            c[i] = c[i] - x[k] * c[i + 1]

    return c
