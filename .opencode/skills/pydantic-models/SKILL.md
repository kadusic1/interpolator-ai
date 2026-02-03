---
name: pydantic-models
description: Guidelines for Pydantic model definitions in the backend
---

## Model Patterns

Use Pydantic v2 patterns with proper type hints:

```python
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator

class InterpolationRequest(BaseModel):
    """Request model for interpolation endpoints."""
    
    points: list[tuple[float, float]] = Field(
        ...,
        min_length=2,
        description="Data points as (x, y) tuples"
    )
    x: float = Field(..., description="X-coordinate to interpolate at")
    method: str = Field(default="lagrange", description="Interpolation method")
    
    @field_validator("points")
    @classmethod
    def validate_unique_x(cls, points: list[tuple[float, float]]):
        x_values = [p[0] for p in points]
        if len(x_values) != len(set(x_values)):
            raise ValueError("X-coordinates must be unique")
        return points
```

## Response Models

```python
class InterpolationResponse(BaseModel):
    """Response model for interpolation results."""
    
    result: float = Field(..., description="Interpolated y-value")
    method: str = Field(..., description="Method used")
    num_points: int = Field(..., description="Number of points used")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"result": 3.25, "method": "lagrange", "num_points": 3}
            ]
        }
    }
```

## Best Practices

1. Always use `Field()` for constraints and descriptions
2. Include `model_config` with JSON examples for API docs
3. Use `from __future__ import annotations` for forward refs
4. Create custom validators for domain-specific rules
5. Follow Google-style docstrings for class documentation
