"""API endpoints for teacher dashboard, cohort analytics, and mastery gap analysis."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from deeptutor.services.cohort.service import get_cohort_service

router = APIRouter(tags=["teacher"])


@router.get("/api/teacher/cohorts")
@router.get("/teacher/cohorts")
async def list_cohorts() -> list[dict[str, Any]]:
    """List available student cohorts."""
    service = get_cohort_service()
    return service.list_cohorts()


@router.get("/api/teacher/cohorts/{cohort_id}/summary")
@router.get("/teacher/cohorts/{cohort_id}/summary")
async def get_cohort_summary(cohort_id: str) -> dict[str, Any]:
    """Retrieve cohort mastery summary, top learning gaps, and frequent misconceptions."""
    service = get_cohort_service()
    try:
        return service.get_cohort_summary(cohort_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/teacher/cohorts/{cohort_id}/heatmap")
@router.get("/teacher/cohorts/{cohort_id}/heatmap")
async def get_cohort_heatmap(cohort_id: str) -> dict[str, Any]:
    """Retrieve student x concept mastery matrix for cohort heatmap visualization."""
    service = get_cohort_service()
    try:
        return service.get_cohort_heatmap(cohort_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/teacher/cohorts/{cohort_id}/gaps")
@router.get("/teacher/cohorts/{cohort_id}/gaps")
async def get_cohort_gaps(cohort_id: str) -> list[dict[str, Any]]:
    """Retrieve ranked weak concepts (class-wide gaps) for the cohort."""
    service = get_cohort_service()
    try:
        return service.get_cohort_gaps(cohort_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
