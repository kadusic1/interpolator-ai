def gauss(A, b, pivot_strategy="scaled", tolerance=1e-10):
    """
    Solve linear equations using Gaussian elimination with partial pivoting.

    Args:
        A: 2D coefficient matrix of linear equations
        b: Array representing constants in equations
        pivot_strategy: Strategy for choosing pivot
            - "scaled": Partial pivoting with scaling (relative ratio)
            - "absolute": Partial pivoting by absolute value
        tolerance: Tolerance for zero detection (default: 1e-10)

    Returns:
        Array containing solution for each variable

    Raises:
        ValueError: If matrix is singular or ill-conditioned
    """
    # Copy matrix A and array b to avoid modifying originals
    A = [row[:] for row in A]
    b = b[:]

    # Number of equations determined by length of b
    num_equations = len(b)

    # Create scaling vector s
    # Scaling vector used for numerical stability.
    # s[i] = max(|a[i][j]|) represents maximum absolute value in row i.
    # Used to choose pivot by relative ratio |a[i][k]|/s[i] instead of
    # just absolute value, avoiding rounding errors.
    # Only used if pivot_strategy="scaled"
    s = []
    if pivot_strategy == "scaled":
        for i in range(num_equations):
            max_value = max(abs(A[i][j]) for j in range(num_equations))
            # Check for zero row to prevent division by zero
            if max_value < tolerance:
                raise ValueError(
                    f"ERROR: Row {i} is effectively zero - matrix is "
                    f"singular!\nmax(|A[{i}][j]|) = {max_value:.2e} < "
                    f"tolerance {tolerance:.2e}"
                )
            s.append(max_value)

    # Gaussian elimination - Transform to upper triangular form

    # Loop through columns of matrix A. Used to choose pivot in each column
    # (diagonal element) and eliminate elements below pivot to get upper
    # triangular form.
    for k in range(num_equations - 1):
        # Find row with largest pivot according to chosen strategy
        # If pivot_strategy="scaled": find row with largest relative ratio
        # If pivot_strategy="absolute": find row with largest absolute value
        # for rows i = k, k+1, ..., n-1
        if pivot_strategy == "scaled":
            max_value = abs(A[k][k]) / s[k] if s[k] > tolerance else 0.0
        else:  # pivot_strategy == "absolute"
            max_value = abs(A[k][k])

        max_row = k

        # Loop through all rows below current row k and find row with
        # largest ratio/value according to chosen strategy
        for i in range(k + 1, num_equations):
            if pivot_strategy == "scaled":
                value = abs(A[i][k]) / s[i] if s[i] > tolerance else 0.0
            else:  # pivot_strategy == "absolute"
                value = abs(A[i][k])

            if value > max_value:
                max_value = value
                max_row = i

        # Swap rows if better pivot found
        if max_row != k:
            A[k], A[max_row] = A[max_row], A[k]
            b[k], b[max_row] = b[max_row], b[k]
            if pivot_strategy == "scaled":
                s[k], s[max_row] = s[max_row], s[k]

        if abs(A[k][k]) < tolerance:
            raise ValueError(
                f"ERROR: Matrix is singular or ill-conditioned!\n"
                f"Pivot A[{k}][{k}] = {A[k][k]:.2e} is less than "
                f"tolerance {tolerance:.2e}\nSystem has no unique solution."
            )

        # Pivoting and elimination
        # Loop through all rows below the pivot row and eliminate all
        # elements below pivot in that column
        for i in range(k + 1, num_equations):
            # Factor represents quotient between element in row i and pivot
            # This factor scales row k to cancel element A[i][k]
            factor = A[i][k] / A[k][k]

            # Loop through columns starting from k and update elements in
            # row i to eliminate A[i][k] (set to 0)
            for j in range(k, num_equations):
                A[i][j] -= factor * A[k][j]

            # Update corresponding element in b array
            b[i] -= factor * b[k]

    # Back substitution

    # Array to store solution for each variable
    # Initialize with zeros
    solution = [0.0] * num_equations

    # Loop starts from last row (lowest equation in triangular form)
    # This order allows solving for solution[i], then using this in
    # subsequent iterations (equations above)
    for i in range(num_equations - 1, -1, -1):
        # Set initial value of solution[i] to corresponding element in b
        # Later adjust by subtracting contributions from already computed
        # variables
        solution[i] = b[i]

        # Loop subtracts elements to the right of solution[i] in current
        # equation, since values for solution[j] (where j > i) are already
        # computed
        for j in range(i + 1, num_equations):
            solution[i] -= A[i][j] * solution[j]

        if abs(A[i][i]) < tolerance:
            raise ValueError(
                f"ERROR: Diagonal element A[{i}][{i}] = {A[i][i]:.2e} is "
                f"less than tolerance!\nSystem has no unique solution."
            )

        # Divide solution[i] by A[i][i] to get final value for x[i]
        solution[i] /= A[i][i]

    return solution
