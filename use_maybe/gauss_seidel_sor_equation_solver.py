from utils.equation_utils import (
    check_diagonal_dominance,
    get_initial_values,
)


def gauss_seidel_sor(A, b, omega=1.0, tolerance=1e-6, max_iterations=800):
    """
    Solve linear equations using Gauss-Seidel with SOR (relaxation).

    Gauss-Seidel method is iterative and:
    1. Uses newest available values in each iteration
    2. Converges faster than Jacobi method
    3. Guaranteed to converge for diagonally dominant matrices

    Relaxation method (SOR - Successive Over-Relaxation):
    - omega = 1.0: Standard Gauss-Seidel
    - 0 < omega < 1: Under-relaxation (helps with oscillations)
    - 1 < omega < 2: Over-relaxation (speeds up convergence)
    - omega >= 2: Method may diverge

    Args:
        A: 2D coefficient matrix of linear equations
        b: Array of constants from right-hand side
        omega: Relaxation coefficient (default: 1.0 - standard Gauss-Seidel)
        tolerance: Error threshold for stopping iterations (default: 1e-6)
        max_iterations: Maximum number of iterations (default: 800)

    Returns:
        Tuple (solution array, number of iterations)

    Raises:
        ValueError: If omega is not in valid range
        ValueError: If matrix A is not diagonally dominant
        ValueError: If diagonal element is zero
    """

    # Check omega parameter - invalid values can cause divergence
    if omega <= 0 or omega >= 2:
        raise ValueError(
            f"ERROR: Relaxation coefficient omega = {omega} is not valid!\n"
            f"Theoretical convergence condition: 0 < omega < 2"
        )

    # Check diagonal dominance - if not satisfied, convergence not guaranteed
    if not check_diagonal_dominance(A):
        raise ValueError(
            "\nConvergence not guaranteed - matrix A is not diagonally "
            "dominant!\nPlease adjust the equation system."
        )

    # Copy data to preserve original A and b
    A = [row[:] for row in A]
    b = b[:]

    # Number of equations/variables
    n = len(b)

    # Generate initial values
    x = get_initial_values(A, b)

    # Store previous values for error calculation
    x_previous = x[:]

    # Iterative process
    for iteration in range(max_iterations):
        # Store current values for error calculation
        x_previous = x[:]

        # Gauss-Seidel with relaxation for each variable
        for i in range(n):
            # Check diagonal element
            if abs(A[i][i]) < 1e-10:
                raise ValueError(
                    f"ERROR: Diagonal element A[{i}][{i}] = {A[i][i]:.2e} "
                    f"is (nearly) zero!\nSystem cannot be solved with "
                    f"Gauss-Seidel.\nReason: avoid division by zero."
                )

            # Calculate residual R_i^(k) per formula (3.118)
            sum_lower = sum(A[i][j] * x[j] for j in range(i))
            sum_upper = sum(A[i][j] * x[j] for j in range(i, n))
            R_i = b[i] - sum_lower - sum_upper

            # SOR formula (3.117): x_i^(k+1) = x_i^(k) + omega * R_i / a_ii
            x[i] = x[i] + omega * (R_i / A[i][i])

        # Maximum error between current and previous iteration
        # Condition (3.105)
        error = max(abs(x[i] - x_previous[i]) for i in range(n))

        # Check convergence
        if error < tolerance:
            return x, iteration + 1

    return x, max_iterations
