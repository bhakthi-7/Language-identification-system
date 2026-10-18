"""FastAPI application exposing the language detector as a REST API.

Run with:  uvicorn api:app --reload
Interactive documentation is served at /docs.
"""

from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import config
from detector import InvalidInputError, get_detector

app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_SUBTITLE,
    version="1.0.0",
)


class IdentifyRequest(BaseModel):
    """Request body for ``POST /identify``."""

    text: str = Field(..., description="Text whose language should be identified.")
    top_n: int = Field(
        config.TOP_N, ge=1, le=10, description="Number of ranked candidates to return."
    )


class CandidateModel(BaseModel):
    code: str
    language: str
    score: float


class IdentifyResponse(BaseModel):
    status: str = Field(..., description="ok, low_confidence or inconclusive")
    language: Optional[str] = None
    code: Optional[str] = None
    score: Optional[float] = Field(
        None, description="Model score of the top candidate (not a calibrated probability)."
    )
    script: Optional[str] = None
    letter_count: int
    candidates: List[CandidateModel]
    warnings: List[str]


@app.get("/health", tags=["system"])
def health() -> Dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/languages", tags=["system"])
def languages() -> Dict[str, str]:
    """List the language codes and names the model can output."""
    return get_detector().supported_languages()


@app.post("/identify", response_model=IdentifyResponse, tags=["detection"])
def identify(request: IdentifyRequest) -> dict:
    """Identify the language of the supplied text.

    Returns HTTP 422 for empty, whitespace-only or over-long text. Inputs that
    are valid but cannot be classified (e.g. only digits) return HTTP 200 with
    ``status`` set to ``inconclusive``.
    """
    try:
        result = get_detector().detect(request.text, top_n=request.top_n)
    except InvalidInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.to_dict()
