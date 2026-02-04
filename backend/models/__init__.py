"""
Purpose: Contains the data structures and type definitions for the application.
This module ensures type safety and validation using Pydantic models and TypedDicts.

Relations:
- Fundamental dependency for `backend.api` (schemas), `backend.agent` (state), and `backend.tools` (inputs/outputs).
"""

from .interpolation import (
    InterpolationRequest,
    InterpolationResponse,
)

__all__ = [
    "InterpolationRequest",
    "InterpolationResponse",
]
