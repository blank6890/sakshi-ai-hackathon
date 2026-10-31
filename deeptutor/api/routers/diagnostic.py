"""API endpoints for adaptive diagnostic testing."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from deeptutor.learning.diagnostic import get_diagnostic_engine

router = APIRouter(tags=["diagnostic"])


class StartDiagnosticRequest(BaseModel):
    syllabus: str = Field(default="class10_physics")


class SubmitAnswersRequest(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)


@router.post("/api/diagnostic/start")
@router.post("/diagnostic/start")
async def start_diagnostic(
    body: StartDiagnosticRequest = Body(default_factory=StartDiagnosticRequest),
) -> dict[str, Any]:
    """Start a new diagnostic assessment session."""
    engine = get_diagnostic_engine()
    session = engine.create_session(syllabus=body.syllabus)
    return session.to_dict()


@router.post("/api/diagnostic/{session_id}/submit")
@router.post("/diagnostic/{session_id}/submit")
async def submit_diagnostic(
    session_id: str,
    body: SubmitAnswersRequest = Body(...),
) -> dict[str, Any]:
    """Submit diagnostic answers, grade, and compute concept mastery vector."""
    engine = get_diagnostic_engine()
    try:
        result = engine.submit_answers(session_id, body.answers)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/diagnostic/{session_id}/report")
@router.get("/diagnostic/{session_id}/report")
async def get_diagnostic_report(session_id: str) -> dict[str, Any]:
    """Retrieve comprehensive diagnostic assessment report."""
    engine = get_diagnostic_engine()
    try:
        report = engine.get_report(session_id)
        return report
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
