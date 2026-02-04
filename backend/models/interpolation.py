from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ValidationInfo


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
    coefficients: list[float] = Field(
        ..., description="Polynomial coefficients [a_0, a_1, ...] in ascending order"
    )

    @field_validator("coefficients")
    def check_coefficients_length(
        cls, coefficients: list[float], info: ValidationInfo
    ) -> list[float]:
        polynomial_degree = info.data.get("polynomial_degree")
        if polynomial_degree is not None and len(coefficients) != polynomial_degree + 1:
            raise ValueError("coefficients length must be polynomial_degree + 1")
        return coefficients

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
