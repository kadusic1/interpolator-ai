def lu_decomposition(A):
    """
    LU decomposition of matrix using Doolittle method.

    Doolittle method: diagonal of matrix L has all elements equal to 1.

    Args:
        A: 2D coefficient matrix of linear equations

    Returns:
        Tuple (L, U) where L is lower triangular, U is upper triangular
    """
    # n represents number of rows (or columns) of matrix A
    # Used for initializing L and U matrices and for algorithm iterations
    n = len(A)

    # Initialize L and U matrices with zeros
    L = [[0.0 for _ in range(n)] for _ in range(n)]
    U = [[0.0 for _ in range(n)] for _ in range(n)]

    # Doolittle algorithm
    for i in range(n):
        # Upper triangular matrix U
        # Formula: u_ij = a_ij - sum(l_ik * u_kj) for k=0 to i-1
        for k in range(i, n):
            if i == 0:
                # Optimization: For first row (i=0), sum is always 0
                U[i][k] = A[i][k]
            else:
                sum_val = 0.0
                for j in range(i):
                    sum_val += L[i][j] * U[j][k]
                U[i][k] = A[i][k] - sum_val

        # Lower triangular matrix L
        for k in range(i, n):
            if i == k:
                # Diagonal of L is always 1 (Doolittle)
                L[i][i] = 1.0
            else:
                if i == 0:
                    # Optimization: For first column, sum is 0
                    if abs(U[0][0]) < 1e-10:
                        raise ValueError(
                            f"ERROR: Diagonal element U[0][0] = {U[0][0]:.2e} "
                            f"is zero!\nLU decomposition does not exist."
                        )
                    L[k][0] = A[k][0] / U[0][0]
                else:
                    # l_ki = (1/u_ii) * (a_ki - sum(l_kj * u_ji)) for j=0 to i-1
                    sum_val = 0.0
                    for j in range(i):
                        sum_val += L[k][j] * U[j][i]
                    if abs(U[i][i]) < 1e-10:
                        raise ValueError(
                            f"ERROR: Diagonal element U[{i}][{i}] = "
                            f"{U[i][i]:.2e} is zero!\n"
                            f"LU decomposition does not exist."
                        )
                    L[k][i] = (A[k][i] - sum_val) / U[i][i]

    return L, U


def forward_substitution(L, b):
    """
    Forward substitution to solve system Ly = b.
    y_0 = b_0
    y_i = b_i - sum(l_ij * y_j) for j=0 to i-1

    Args:
        L: Lower triangular matrix
        b: Constants vector

    Returns:
        Vector y which is the solution to system Ly = b
    """
    n = len(b)
    # Initialize vector y with zeros
    y = [0.0] * n

    # Iterate through all rows of matrix L (first to last)
    for i in range(n):
        if i == 0:
            # Optimization: For first element (i=0), sum is 0 (no prior elements)
            # Directly set y[0] = b[0] (since L[0][0] = 1 in Doolittle method)
            y[0] = b[0]
        else:
            # Calculate sum l_ij * y_j for all known y[j] (j < i)
            sum_val = 0.0
            for j in range(i):
                sum_val += L[i][j] * y[j]
            # For Doolittle method, L[i][i] = 1, so no division needed
            # Formula: y[i] = (b[i] - sum) / L[i][i], but since L[i][i] = 1
            # we get y[i] = b[i] - sum
            y[i] = b[i] - sum_val

    return y


def backward_substitution(U, y):
    """
    Backward substitution to solve system Ux = y.
    x_{n-1} = y_{n-1} / u_{n-1,n-1}
    x_i = (1/u_ii) * (y_i - sum(u_ij * x_j)) for j=i+1 to n-1

    Args:
        U: Upper triangular matrix
        y: Vector obtained from forward substitution

    Returns:
        Vector x which is the final solution to the system
    """
    n = len(y)
    # Initialize vector x with zeros
    x = [0.0] * n

    # Iterate backward through all rows of matrix U (last to first)
    for i in range(n - 1, -1, -1):
        if i == n - 1:
            # Optimization: For last element (i=n-1), sum is 0 (no elements to right)
            # Check if diagonal element is non-zero
            if abs(U[i][i]) < 1e-10:
                raise ValueError(
                    f"ERROR: Diagonal element U[{i}][{i}] = {U[i][i]:.2e} "
                    f"is zero!\nSystem has no unique solution."
                )
            # Directly compute x[n-1] = y[n-1] / u[n-1][n-1]
            x[i] = y[i] / U[i][i]
        else:
            # Calculate sum u_ij * x_j for all known x[j] (j > i)
            sum_val = 0.0
            for j in range(i + 1, n):
                sum_val += U[i][j] * x[j]
            # Check if diagonal element is non-zero
            if abs(U[i][i]) < 1e-10:
                raise ValueError(
                    f"ERROR: Diagonal element U[{i}][{i}] = {U[i][i]:.2e} "
                    f"is zero!\nSystem has no unique solution."
                )
            # Formula: x[i] = (y[i] - sum) / u[i][i]
            x[i] = (y[i] - sum_val) / U[i][i]

    return x


def doolittle(A, b):
    """
    Main function to solve linear equations using LU decomposition
    (Doolittle method).

    Solution process:
    1. A = LU (decomposition)
    2. Ly = b (forward substitution)
    3. Ux = y (backward substitution)

    Args:
        A: 2D coefficient matrix of linear equations
        b: Constants vector

    Returns:
        Tuple (x, L, U) where x is solution to system Ax = b
    """
    # Copy matrix A and vector b to avoid modifying originals
    A = [row[:] for row in A]
    b = b[:]

    # Step 1: LU decomposition
    L, U = lu_decomposition(A)

    # Step 2: Forward substitution (Ly = b)
    y = forward_substitution(L, b)

    # Step 3: Backward substitution (Ux = y)
    x = backward_substitution(U, y)

    return x, L, U
