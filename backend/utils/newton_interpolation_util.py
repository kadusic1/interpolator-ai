from __future__ import annotations

import math


def validate_equidistant(x_values: list[float], tolerance: float = 1e-9) -> float:
    """Validate that x-values are equidistant and return step size.

    Args:
        x_values: List of x-coordinates (should be sorted).
        tolerance: Maximum allowed deviation from constant step size.

    Returns:
        The step size h = x_{i+1} - x_i.

    Raises:
        ValueError: If fewer than 2 points or points are not equidistant.

    Example:
        >>> validate_equidistant([1.0, 2.0, 3.0, 4.0])
        1.0
        >>> validate_equidistant([1.0, 2.0, 3.1, 4.0])
        ValueError: Points must be equidistant for Newton interpolation
    """
    if len(x_values) < 2:
        raise ValueError("At least 2 points required for equidistant validation.")

    # Compute all step sizes
    steps = [x_values[i + 1] - x_values[i] for i in range(len(x_values) - 1)]

    # Get reference step size
    h = steps[0]

    # Check all steps are approximately equal to h
    for i, step in enumerate(steps):
        if abs(step - h) > tolerance:
            raise ValueError(
                f"Points must be equidistant for Newton interpolation. "
                f"Step at index {i}: {step:.10f}, expected: {h:.10f}, "
                f"difference: {abs(step - h):.2e}"
            )

    return h


def compute_difference_table(y_values: list[float]) -> list[list[float]]:
    """Build the full forward difference table.

    Constructs a triangular table where table[k][j] represents Δᵏf_j,
    the k-th forward difference at position j.

    Forward difference formula:
        Δ⁰f_j = f_j (original values)
        Δ¹f_j = f_{j+1} - f_j
        Δᵏf_j = Δᵏ⁻¹f_{j+1} - Δᵏ⁻¹f_j

    Args:
        y_values: List of y-coordinates [f_0, f_1, ..., f_n].

    Returns:
        2D list where table[k] is the k-th difference level:
            table[0] = [f_0, f_1, f_2, f_3]     (original values)
            table[1] = [Δf_0, Δf_1, Δf_2]       (1st differences)
            table[2] = [Δ²f_0, Δ²f_1]           (2nd differences)
            table[3] = [Δ³f_0]                  (3rd differences)

    Example:
        >>> compute_difference_table([1.0, 2.0, 4.0, 7.0])
        [[1.0, 2.0, 4.0, 7.0], [1.0, 2.0, 3.0], [1.0, 1.0], [0.0]]
    """
    n = len(y_values)
    table = [y_values.copy()]  # Level 0: original values

    # Build successive difference levels
    for level in range(1, n):
        prev_level = table[level - 1]
        current_level = []

        # Compute differences: Δᵏf_j = Δᵏ⁻¹f_{j+1} - Δᵏ⁻¹f_j
        for j in range(len(prev_level) - 1):
            diff = prev_level[j + 1] - prev_level[j]
            current_level.append(diff)

        table.append(current_level)

    return table


def forward_binomial_coefficient(s: float, k: int) -> float:
    """Compute forward binomial coefficient (s choose k).

    Formula from equation (4.27):
        (s, k) = s(s-1)(s-2)...(s-k+1) / k!

    This is the generalized binomial coefficient for Newton forward
    interpolation.

    Args:
        s: The interpolation parameter s = (x - x₀) / h.
        k: The order of the binomial coefficient.

    Returns:
        The value of (s choose k).

    Example:
        >>> forward_binomial_coefficient(0.4, 1)
        0.4
        >>> forward_binomial_coefficient(0.4, 2)
        -0.12
    """
    if k == 0:
        return 1.0

    # Compute numerator: s(s-1)(s-2)...(s-k+1)
    numerator = 1.0
    for i in range(k):
        numerator *= s - i

    # Divide by k!
    return numerator / math.factorial(k)


def backward_binomial_coefficient(s: float, k: int) -> float:
    """Compute backward binomial coefficient (s⁺ choose k).

    Formula from equation (4.34):
        (s⁺, k) = s(s+1)(s+2)...(s+k-1) / k!

    This is used in Newton backward interpolation where the binomial
    has positive increments instead of negative.

    Args:
        s: The interpolation parameter s = (x - x₀) / h.
        k: The order of the binomial coefficient.

    Returns:
        The value of (s⁺ choose k).

    Example:
        >>> backward_binomial_coefficient(-0.6, 1)
        -0.6
        >>> backward_binomial_coefficient(-0.6, 2)
        0.12
    """
    if k == 0:
        return 1.0

    # Compute numerator: s(s+1)(s+2)...(s+k-1)
    numerator = 1.0
    for i in range(k):
        numerator *= s + i

    # Divide by k!
    return numerator / math.factorial(k)


def select_optimal_x0_index(x_values: list[float], x_eval: float, method: str) -> int:
    """Select optimal starting index for Newton interpolation.

    Strategy:
    - Forward method: Choose x₀ where x_eval is close to or ahead of x₀
      (interpolating from the beginning)
    - Backward method: Choose x₀ where x_eval is close to or behind x₀
      (interpolating from the end)

    Args:
        x_values: Sorted list of x-coordinates.
        x_eval: The x value to interpolate at.
        method: Either "forward" or "backward".

    Returns:
        The optimal index for x₀.

    Raises:
        ValueError: If method is not "forward" or "backward".

    Example:
        >>> x_vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        >>> select_optimal_x0_index(x_vals, 2.3, "forward")
        1  # x₀ = 2.0, interpolating forward
        >>> select_optimal_x0_index(x_vals, 2.3, "backward")
        2  # x₀ = 3.0, interpolating backward
    """
    if method not in ["forward", "backward"]:
        raise ValueError(f"Method must be 'forward' or 'backward', got: {method}")

    n = len(x_values)

    # Find where x_eval falls in the range
    if x_eval <= x_values[0]:
        # x_eval is before or at the first point
        return 0 if method == "forward" else min(1, n - 1)
    elif x_eval >= x_values[-1]:
        # x_eval is after or at the last point
        return max(0, n - 2) if method == "forward" else n - 1
    else:
        # x_eval is within the range
        # Find the interval [x_i, x_{i+1}] containing x_eval
        for i in range(n - 1):
            if x_values[i] <= x_eval <= x_values[i + 1]:
                if method == "forward":
                    # Use the left endpoint
                    return i
                else:
                    # Use the right endpoint
                    return i + 1

        # Fallback (should not reach here)
        return 0 if method == "forward" else n - 1
