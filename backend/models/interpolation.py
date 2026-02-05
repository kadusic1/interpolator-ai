from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ValidationInfo


class InterpolationRequest(BaseModel):
    """Generic request model for all interpolation methods."""

    points: list[tuple[float, float]] = Field(
        ..., min_length=2, description="Data points as (x, y) tuples"
    )
    x_evals: list[float] | None = Field(
        None, description="Optional X-coordinates to interpolate at"
    )
    method: str = Field(..., description="Interpolation method name")


class InterpolationRequestList(BaseModel):
    """Container for multiple interpolation requests."""

    requests: list[InterpolationRequest] = Field(
        ..., description="List of interpolation requests"
    )
    is_interpolation_request: bool = Field(
        True,
        description="False if the user input is completely unrelated to interpolation",
    )
    clarification_message: str | None = Field(
        None, description="Message to user if request is invalid or unrelated"
    )


class InterpolationResponse(BaseModel):
    """Base response model for all interpolation methods."""

    results: list[float] | None = Field(
        None, description="Interpolated y-values at x_evals"
    )
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
                    "results": [3.25],
                    "coefficients": [1.0, 0.5, 1.0],
                    "polynomial_degree": 2,
                }
            ]
        }
    }


class InterpolationResponseWithMetadata(InterpolationResponse):
    """Response model including the polynomial graph."""

    points: list[tuple[float, float]] = Field(
        ..., min_length=2, description="Data points as (x, y) tuples"
    )
    method: str = Field(..., description="Interpolation method name")
    image_base64: str = Field(
        ..., description="Base64 encoded PNG image of the polynomial graph"
    )

    @field_validator("points", "coefficients", mode="after")
    @classmethod
    def round_values(cls, v: Any) -> Any:
        if isinstance(v, list) and len(v) > 0:
            # Handle list of tuples (points)
            if isinstance(v[0], tuple):
                return [(round(p[0], 6), round(p[1], 6)) for p in v]
            # Handle list of floats (coefficients)
            return [round(x, 6) for x in v]
        return v
