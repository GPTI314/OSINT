"""Report endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import os

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst, get_pagination_params
from app.models.user import User
from app.models.report import Report
from app.models.investigation import Investigation
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse, ReportExportRequest
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report"""
    # Verify investigation exists
    result = await db.execute(
        select(Investigation).where(Investigation.id == report_data.investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    new_report = Report(
        **report_data.model_dump(),
        created_by=current_user.id
    )

    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    return new_report


@router.get("/", response_model=PaginatedResponse[ReportResponse])
async def list_reports(
    investigation_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    format_filter: Optional[str] = Query(None, alias="format"),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List reports with filtering"""
    query = select(Report)

    # Apply filters
    if investigation_id:
        query = query.where(Report.investigation_id == investigation_id)
    if status_filter:
        query = query.where(Report.status == status_filter)
    if format_filter:
        query = query.where(Report.format == format_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(pagination["offset"]).limit(pagination["page_size"])
    result = await db.execute(query)
    reports = result.scalars().all()

    return {
        "items": reports,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report by ID"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update report"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    # Update report
    for field, value in report_data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)

    await db.commit()
    await db.refresh(report)

    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Delete report"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    # Delete file if exists
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)

    await db.delete(report)
    await db.commit()

    return None


@router.post("/{report_id}/generate", response_model=ReportResponse)
async def generate_report(
    report_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Generate report file"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    from app.models.report import ReportStatus
    from datetime import datetime

    report.status = ReportStatus.GENERATING

    await db.commit()

    # TODO: Trigger actual report generation task via Celery
    # This would generate PDF, HTML, Excel, etc.

    # For now, just mark as completed
    report.status = ReportStatus.COMPLETED
    report.generated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(report)

    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Download generated report file"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found. Please generate the report first.",
        )

    return FileResponse(
        path=report.file_path,
        filename=f"{report.title}.{report.format.value}",
        media_type="application/octet-stream"
    )
