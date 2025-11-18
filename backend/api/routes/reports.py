"""
Report generation endpoints for OSINT investigations.
"""
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime

from models.user import User
from api.routes.auth import get_current_user

router = APIRouter()


class ReportRequest(BaseModel):
    """Report generation request schema."""
    investigation_id: int
    format: Literal["pdf", "json", "csv", "xlsx"] = "pdf"
    include_targets: bool = True
    include_results: bool = True
    include_analysis: bool = True


@router.post("/generate")
async def generate_report(
    report_request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a report for an investigation.

    Args:
        report_request: Report configuration
        current_user: Current authenticated user

    Returns:
        dict: Report generation task ID
    """
    return {
        "task_id": f"report_{datetime.utcnow().timestamp()}",
        "status": "generating",
        "format": report_request.format,
        "investigation_id": report_request.investigation_id
    }


@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a generated report.

    Args:
        report_id: Report ID
        current_user: Current authenticated user

    Returns:
        Response: Report file
    """
    # This will return the actual file
    return {
        "report_id": report_id,
        "download_url": f"/reports/{report_id}/file"
    }
