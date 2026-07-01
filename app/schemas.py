"""Pydantic request and response schemas for the API."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class EmailRequest(BaseModel):
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class EmailAnalysis(BaseModel):
    category: str
    priority: str
    client_name: str | None
    company: str | None
    summary: str
    budget: str | None
    deadline: str | None
    needs_reply: bool
    reply_draft: str
    tags: list[str]
    recommended_action: str

    @field_validator("budget", "deadline", mode="before")
    @classmethod
    def stringify_numeric_values(cls, value: Any) -> Any:
        """Normalize occasional numeric values returned by a local LLM."""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
        return value


class EmailAnalysisResponse(EmailAnalysis):
    id: int


class EmailAnalysisSaved(EmailAnalysis):
    id: int
    created_at: str
    subject: str
    body: str


class ErrorResponse(BaseModel):
    error: str
    details: str | None = None
