"""FastAPI entry point for the AI Email Automation Agent."""

import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import ValidationError

from app.crud import (
    get_email_analysis_by_id,
    get_email_history,
    save_email_analysis,
)
from app.database import init_db
from app.llm_client import (
    OllamaError,
    OllamaInvalidResponseError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    OllamaUnavailableError,
    analyze_email_with_ollama,
)
from app.schemas import (
    EmailAnalysis,
    EmailAnalysisResponse,
    EmailAnalysisSaved,
    EmailRequest,
    ErrorResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Email Automation Agent",
    description="Local business email analysis powered by Ollama.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "AI Email Automation Agent"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/analyze-email",
    response_model=EmailAnalysisResponse,
    responses={
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def analyze_email(email: EmailRequest) -> EmailAnalysisResponse:
    try:
        analysis = analyze_email_with_ollama(email.subject, email.body)
        validated_analysis = EmailAnalysis(**analysis)
        analysis_data = validated_analysis.model_dump()
        analysis_id = save_email_analysis(email.subject, email.body, analysis_data)
        return EmailAnalysisResponse(id=analysis_id, **analysis_data)
    except OllamaTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except (OllamaUnavailableError, OllamaModelNotFoundError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OllamaInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"The model response does not match the expected schema: {exc}",
        ) from exc
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save the email analysis: {exc}",
        ) from exc


@app.get("/history", response_model=list[EmailAnalysisSaved])
def history(limit: int = Query(default=10, ge=1, le=100)) -> list[dict]:
    try:
        return get_email_history(limit)
    except (sqlite3.Error, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load email history: {exc}",
        ) from exc


@app.get("/history/{analysis_id}", response_model=EmailAnalysisSaved)
def history_item(analysis_id: int) -> dict:
    try:
        record = get_email_analysis_by_id(analysis_id)
    except (sqlite3.Error, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load the email analysis: {exc}",
        ) from exc

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Email analysis with id {analysis_id} was not found.",
        )
    return record
