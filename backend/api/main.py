from typing import List, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent.pipeline import process_request
from backend.models.interpolation import InterpolationResponseWithMetadata

app = FastAPI(title="Interpolation Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentQuery(BaseModel):
    user_input: str
    image_base64: str | None = None
    method: str = "lagrange"  # Default method


@app.post(
    "/process", response_model=Union[List[InterpolationResponseWithMetadata], str]
)
def process_interpolation(query: AgentQuery):
    try:
        # Using standard 'def' to run sync blocking code in threadpool
        return process_request(
            user_input=query.user_input,
            image_base64=query.image_base64,
            method=query.method,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
