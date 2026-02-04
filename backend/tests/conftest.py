"""Shared fixtures for interpolation tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def linear_points() -> list[tuple[float, float]]:
    """Two equidistant points defining P(x) = 1 + 2x."""
    return [(0.0, 1.0), (2.0, 5.0)]


@pytest.fixture
def quadratic_points() -> list[tuple[float, float]]:
    """Three equidistant points defining P(x) = 1 + x²."""
    return [(0.0, 1.0), (1.0, 2.0), (2.0, 5.0)]


@pytest.fixture
def non_equidistant_points() -> list[tuple[float, float]]:
    """Three non-equidistant points (for Lagrange/Direct only)."""
    return [(0.0, 1.0), (1.0, 2.0), (3.0, 10.0)]
