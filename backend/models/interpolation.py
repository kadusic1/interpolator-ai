from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class InterpolationRequest(BaseModel):
    """Generic request model for all interpolation methods."""

    points: list[tuple[float, float]] = Field(
        ..., min_length=2, description="Data points as (x, y) tuples"
    )
    x_eval: float = Field(..., description="X-coordinate to interpolate at")

    @field_validator("points")
    @classmethod
    def validate_unique_x(
        cls, points: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        """Validate that all x-coordinates are unique."""
        x_values = [p[0] for p in points]
        if len(x_values) != len(set(x_values)):
            raise ValueError("X-coordinates must be unique")
        return points


class InterpolationResponse(BaseModel):
    """Base response model for all interpolation methods."""

    result: float = Field(..., description="Interpolated y-value at x_eval")
    polynomial_degree: int = Field(
        ..., description="Degree of the interpolating polynomial"
    )


class DirectInterpolationResponse(InterpolationResponse):
    """Response model for direct interpolation with coefficients."""

    coefficients: list[float] = Field(
        ..., description="Polynomial coefficients [a_0, a_1, ...] in ascending order"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": 3.25,
                    "coefficients": [1.0, 0.5, 1.0],
                    "polynomial_degree": 2,
                }
            ]
        }
    }


class LagrangeInterpolationResponse(InterpolationResponse):
    """Response model for Lagrange interpolation with basis values."""

    basis_values: list[float] = Field(
        ...,
        description="Lagrange basis polynomial values [L_0(x_eval), ..., L_n(x_eval)]",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": 3.25,
                    "basis_values": [0.125, 0.75, 0.125],
                    "polynomial_degree": 2,
                }
            ]
        }
    }


class NewtonForwardInterpolationResponse(InterpolationResponse):
    """Response model for Newton forward difference interpolation."""

    difference_table: list[list[float]] = Field(
        ...,
        description="Full forward difference table [Δ⁰f, Δ¹f, Δ²f, ...]",
    )
    step_size: float = Field(..., description="Equidistant step size h = x_{i+1} - x_i")
    s_parameter: float = Field(
        ..., description="Interpolation variable s = (x - x₀) / h"
    )
    x0: float = Field(..., description="Starting point x₀ used in interpolation")
    x0_index: int = Field(..., description="Index of x₀ in the original points array")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": 0.290698,
                    "difference_table": [
                        [0.294118, 0.285714, 0.277778],
                        [-0.008404, -0.007936],
                        [0.000468],
                    ],
                    "step_size": 0.1,
                    "s_parameter": 0.4,
                    "x0": 3.4,
                    "x0_index": 0,
                    "polynomial_degree": 2,
                }
            ]
        }
    }


class NewtonBackwardInterpolationResponse(InterpolationResponse):
    """Response model for Newton backward difference interpolation."""

    difference_table: list[list[float]] = Field(
        ...,
        description="Full forward difference table [Δ⁰f, Δ¹f, Δ²f, ...]",
    )
    step_size: float = Field(..., description="Equidistant step size h")
    s_parameter: float = Field(
        ...,
        description="Interpolation variable s = (x - x₀) / h (typically negative)",
    )
    x0: float = Field(..., description="Reference point x₀ used in interpolation")
    x0_index: int = Field(..., description="Index of x₀ in the original points array")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": 0.290698,
                    "difference_table": [
                        [0.294118, 0.285714, 0.277778],
                        [-0.008404, -0.007936],
                        [0.000468],
                    ],
                    "step_size": 0.1,
                    "s_parameter": -0.6,
                    "x0": 3.5,
                    "x0_index": 1,
                    "polynomial_degree": 2,
                }
            ]
        }
    }
