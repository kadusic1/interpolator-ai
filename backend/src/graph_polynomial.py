from __future__ import annotations

import base64
import io

import matplotlib.pyplot as plt
import numpy as np

from backend.utils.general_util import evaluate_polynomial, get_polynomial_string


def graph_polynomial(
    coefficients: list[float], points: list[tuple[float, float]]
) -> dict:
    """
    Generate a matplotlib graph of a polynomial function with data points.

    Creates a mathematical-style plot showing the polynomial curve and the
    original data points used for interpolation. The graph is returned as
    a base64-encoded PNG image suitable for display in web frontends.

    Args:
        coefficients: Polynomial coefficients [a_0, a_1, ...] in ascending
            power order where P(x) = a_0 + a_1*x + a_2*x^2 + ...
        points: Original data points as (x, y) tuples used for markers
            and automatic range calculation.

    Returns:
        Dictionary containing:
            - 'image_base64': PNG image encoded as base64 string
            - 'mime_type': Always 'image/png'

    Example:
        >>> coeffs = [1.0, 0.0, 1.0]  # P(x) = 1 + x²
        >>> pts = [(0, 1), (1, 2), (2, 5)]
        >>> result = graph_polynomial(coeffs, pts)
        >>> result.keys()
        dict_keys(['image_base64', 'mime_type'])
    """
    # Extract x and y coordinates from points
    x_points = [p[0] for p in points]
    y_points = [p[1] for p in points]

    # Calculate x-range with 10% margin on each side
    x_min = min(x_points)
    x_max = max(x_points)
    margin = x_max - x_min
    x_range_start = x_min - margin
    x_range_end = x_max + margin

    # Generate smooth curve with 200 points
    x_curve = np.linspace(x_range_start, x_range_end, 200)
    y_curve = np.array([evaluate_polynomial(coefficients, x) for x in x_curve])

    # Calculate y-range with 15% margin to prevent cutoff
    all_y_values = np.concatenate([y_curve, y_points])
    y_min = np.min(all_y_values)
    y_max = np.max(all_y_values)
    y_margin = (y_max - y_min) * 0.15
    y_range_start = y_min - y_margin
    y_range_end = y_max + y_margin

    # Create figure and plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot polynomial curve
    polynomial_string = get_polynomial_string(coefficients)
    breakpoint()
    ax.plot(x_curve, y_curve, "b-", linewidth=2, label=polynomial_string)

    # Plot original data points
    ax.scatter(x_points, y_points, color="red", s=50, zorder=5, label="Data points")

    # Set axis limits to ensure full visibility
    ax.set_xlim(x_range_start, x_range_end)
    ax.set_ylim(y_range_start, y_range_end)

    # Add grid
    ax.grid(True, alpha=0.3)

    # Add axes through origin (only if 0 is within range)
    if y_range_start <= 0 <= y_range_end:
        ax.axhline(y=0, color="k", linewidth=1.5)
    if x_range_start <= 0 <= x_range_end:
        ax.axvline(x=0, color="k", linewidth=1.5)

    # Labels and legend
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()

    # Convert to base64-encoded PNG
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)

    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {"image_base64": image_base64, "mime_type": "image/png"}
