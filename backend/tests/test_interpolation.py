"""Unit tests for all 4 interpolation methods."""

from __future__ import annotations

import pytest

from backend.src.direct_interpolation import direct_interpolation
from backend.src.lagrange_interpolation import lagrange_interpolation
from backend.src.newton_backward_interpolation import newton_backward_interpolation
from backend.src.newton_forward_interpolation import newton_forward_interpolation

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
        # Test single point
        result = method(linear_points, [1.0])
        assert result["results"][0] == pytest.approx(3.0, rel=1e-6)

        # Test multiple points
        result_multi = method(linear_points, [0.0, 1.0, 2.0])
        expected = [1.0, 3.0, 5.0]
        assert result_multi["results"] == pytest.approx(expected, rel=1e-6)

    @pytest.mark.parametrize("method", NON_EQUIDISTANT_METHODS)
    def test_quadratic_interpolation(self, method, quadratic_points):
        """Direct and Lagrange interpolate quadratic correctly anywhere."""
        result = method(quadratic_points, [1.5])
        assert result["results"][0] == pytest.approx(3.25, rel=1e-6)

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_interpolation_at_node(self, method, quadratic_points):
        """Interpolation at a data point returns exact value."""
        # Test all original x points
        x_vals = [p[0] for p in quadratic_points]
        y_vals = [p[1] for p in quadratic_points]

        result = method(quadratic_points, x_vals)
        assert result["results"] == pytest.approx(y_vals, rel=1e-9)

    def test_newton_forward_accuracy(self, quadratic_points):
        """Newton forward matches expected values."""
        # P(x) = 1 + x^2
        # Check a few points
        x_test = [0.5, 1.5]
        expected = [1.25, 3.25]

        result = newton_forward_interpolation(quadratic_points, x_test)
        assert result["results"] == pytest.approx(expected, rel=1e-6)

    def test_newton_backward_accuracy(self, quadratic_points):
        """Newton backward matches expected values."""
        # P(x) = 1 + x^2
        x_test = [0.5, 1.5]
        expected = [1.25, 3.25]

        result = newton_backward_interpolation(quadratic_points, x_test)
        assert result["results"] == pytest.approx(expected, rel=1e-6)

    @pytest.mark.parametrize("method", NON_EQUIDISTANT_METHODS)
    def test_methods_agree(self, method, quadratic_points):
        """Direct and Lagrange produce the same result."""
        x_evals = [0.75, 1.25]
        expected = [1.0 + x**2 for x in x_evals]  # P(x) = 1 + x²

        result = method(quadratic_points, x_evals)
        assert result["results"] == pytest.approx(expected, rel=1e-6)


class TestResponseStructure:
    """Tests for correct response format."""

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_response_keys(self, method, quadratic_points):
        """Response contains required keys."""
        result = method(quadratic_points, [1.0])
        assert "results" in result
        assert "coefficients" in result
        assert "polynomial_degree" in result

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_polynomial_degree(self, method, quadratic_points):
        """Polynomial degree equals n-1 for n points."""
        result = method(quadratic_points, [1.0])
        assert result["polynomial_degree"] == len(quadratic_points) - 1

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_coefficients_length(self, method, quadratic_points):
        """Coefficients length equals polynomial_degree + 1."""
        result = method(quadratic_points, [1.0])
        assert len(result["coefficients"]) == result["polynomial_degree"] + 1

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_none_evaluation(self, method, quadratic_points):
        """Test handling of None for x_evals."""
        result = method(quadratic_points, None)
        assert result["results"] is None
        assert len(result["coefficients"]) > 0


class TestErrorHandling:
    """Tests for proper error handling."""

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_insufficient_points(self, method):
        """Raises ValueError with fewer than 2 points."""
        with pytest.raises(ValueError, match="[Aa]t least 2 points"):
            method([(1.0, 1.0)], [1.0])

    @pytest.mark.parametrize("method", ALL_METHODS)
    def test_duplicate_x_coordinates(self, method):
        """Raises ValueError for duplicate x-coordinates."""
        points = [(1.0, 2.0), (1.0, 3.0), (2.0, 4.0)]
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            method(points, [1.5])

    @pytest.mark.parametrize("method", NEWTON_METHODS)
    def test_non_equidistant_newton(self, method, non_equidistant_points):
        """Newton methods raise ValueError for non-equidistant points."""
        with pytest.raises(ValueError, match="equidistant"):
            method(non_equidistant_points, [2.0])


class TestNonEquidistant:
    """Tests for methods that support non-equidistant points."""

    @pytest.mark.parametrize("method", NON_EQUIDISTANT_METHODS)
    def test_non_equidistant_interpolation(self, method, non_equidistant_points):
        """Lagrange and Direct work with non-equidistant points."""
        result = method(non_equidistant_points, [2.0])
        assert "results" in result
        assert isinstance(result["results"], list)
