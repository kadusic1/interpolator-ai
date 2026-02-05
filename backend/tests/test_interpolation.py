"""Unit tests for all 4 interpolation methods."""

from __future__ import annotations

import pytest

from backend.src import (
    direct_interpolation,
    lagrange_interpolation,
    newton_backward_interpolation,
    newton_forward_interpolation,
)

# All methods for parametrized tests
ALL_METHODS = [
    direct_interpolation,
    lagrange_interpolation,
    newton_forward_interpolation,
    newton_backward_interpolation,
]

# Methods that work with non-equidistant points
NON_EQUIDISTANT_METHODS = [
    direct_interpolation,
    lagrange_interpolation,
]

# Methods requiring equidistant points
NEWTON_METHODS = [
    newton_forward_interpolation,
    newton_backward_interpolation,
]


class TestHappyPath:
    """Tests for correct interpolation results."""

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_linear_interpolation(self, method, linear_points):
        """All methods interpolate linear function correctly."""
        result = method.invoke({"points": linear_points, "x_eval": 1.0})
        assert result["result"] == pytest.approx(3.0, rel=1e-6)

    @pytest.mark.parametrize("method", NON_EQUIDISTANT_METHODS)
    def test_quadratic_interpolation(self, method, quadratic_points):
        """Direct and Lagrange interpolate quadratic correctly anywhere."""
        result = method.invoke({"points": quadratic_points, "x_eval": 1.5})
        assert result["result"] == pytest.approx(3.25, rel=1e-6)

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_interpolation_at_node(self, method, quadratic_points):
        """Interpolation at a data point returns exact value."""
        result = method.invoke({"points": quadratic_points, "x_eval": 1.0})
        assert result["result"] == pytest.approx(2.0, rel=1e-9)

    def test_newton_forward_near_start(self, quadratic_points):
        """Newton forward is accurate near the beginning of data."""
        result = newton_forward_interpolation.invoke(
            {"points": quadratic_points, "x_eval": 0.5}
        )
        expected = 1.0 + 0.5**2  # P(x) = 1 + x²
        assert result["result"] == pytest.approx(expected, rel=1e-6)

    def test_newton_backward_near_end(self, quadratic_points):
        """Newton backward is accurate near the end of data."""
        result = newton_backward_interpolation.invoke(
            {"points": quadratic_points, "x_eval": 1.5}
        )
        expected = 1.0 + 1.5**2  # P(x) = 1 + x²
        assert result["result"] == pytest.approx(expected, rel=1e-6)

    @pytest.mark.parametrize("method", NON_EQUIDISTANT_METHODS)
    def test_methods_agree(self, method, quadratic_points):
        """Direct and Lagrange produce the same result."""
        x_eval = 0.75
        expected = 1.0 + 0.75**2  # P(x) = 1 + x²
        result = method.invoke({"points": quadratic_points, "x_eval": x_eval})
        assert result["result"] == pytest.approx(expected, rel=1e-6)


class TestResponseStructure:
    """Tests for correct response format."""

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_response_keys(self, method, quadratic_points):
        """Response contains required keys."""
        result = method.invoke({"points": quadratic_points, "x_eval": 1.0})
        assert "result" in result
        assert "coefficients" in result
        assert "polynomial_degree" in result

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_polynomial_degree(self, method, quadratic_points):
        """Polynomial degree equals n-1 for n points."""
        result = method.invoke({"points": quadratic_points, "x_eval": 1.0})
        assert result["polynomial_degree"] == len(quadratic_points) - 1

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_coefficients_length(self, method, quadratic_points):
        """Coefficients length equals polynomial_degree + 1."""
        result = method.invoke({"points": quadratic_points, "x_eval": 1.0})
        assert len(result["coefficients"]) == result["polynomial_degree"] + 1


class TestErrorHandling:
    """Tests for proper error handling."""

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_insufficient_points(self, method):
        """Raises ValueError with fewer than 2 points."""
        with pytest.raises(ValueError, match="[Aa]t least 2 points"):
            method.invoke({"points": [(1.0, 1.0)], "x_eval": 1.0})

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_duplicate_x_coordinates(self, method):
        """Raises ValueError for duplicate x-coordinates."""
        points = [(1.0, 2.0), (1.0, 3.0), (2.0, 4.0)]
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            method.invoke({"points": points, "x_eval": 1.5})

    @pytest.mark.parametrize("method", NEWTON_METHODS)
    def test_non_equidistant_newton(self, method, non_equidistant_points):
        """Newton methods raise ValueError for non-equidistant points."""
        with pytest.raises(ValueError, match="equidistant"):
            method.invoke({"points": non_equidistant_points, "x_eval": 2.0})


class TestNonEquidistant:
    """Tests for methods that support non-equidistant points."""

    @pytest.mark.parametrize("method", NON_EQUIDISTANT_METHODS)
    def test_non_equidistant_interpolation(self, method, non_equidistant_points):
        """Lagrange and Direct work with non-equidistant points."""
        result = method.invoke({"points": non_equidistant_points, "x_eval": 2.0})
        assert "result" in result
        assert isinstance(result["result"], float)
