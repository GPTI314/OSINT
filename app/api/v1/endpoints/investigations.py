"""Investigation endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst, get_pagination_params
from app.models.user import User
from app.models.investigation import Investigation
from app.schemas.investigation import InvestigationCreate, InvestigationUpdate, InvestigationResponse, InvestigationStats
from app.schemas.common import PaginatedResponse
from app.core.rate_limit import limiter
from fastapi import Request
import uuid

router = APIRouter()


@router.post("/", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation_data: InvestigationCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Create a new investigation"""
    # Generate unique case number
    case_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

    new_investigation = Investigation(
        **investigation_data.model_dump(),
        case_number=case_number,
        created_by=current_user.id
    )

    db.add(new_investigation)
    await db.commit()
    await db.refresh(new_investigation)

    return new_investigation


@router.get("/", response_model=PaginatedResponse[InvestigationResponse])
@limiter.limit("60/minute")
async def list_investigations(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    search: Optional[str] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List investigations with filtering and pagination"""
    query = select(Investigation)

    # Apply filters
    if status_filter:
        query = query.where(Investigation.status == status_filter)
    if priority_filter:
        query = query.where(Investigation.priority == priority_filter)
    if search:
        query = query.where(
            or_(
                Investigation.title.ilike(f"%{search}%"),
                Investigation.case_number.ilike(f"%{search}%"),
                Investigation.description.ilike(f"%{search}%")
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(pagination["offset"]).limit(pagination["page_size"])
    result = await db.execute(query)
    investigations = result.scalars().all()

    return {
        "items": investigations,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investigation by ID"""
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    return investigation


@router.get("/{investigation_id}/stats", response_model=InvestigationStats)
async def get_investigation_stats(
    investigation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investigation statistics"""
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    # Get counts from relationships
    from app.models.finding import Finding, FindingSeverity

    stats = InvestigationStats()
    stats.total_targets = len(investigation.targets)
    stats.total_scraping_jobs = len(investigation.scraping_jobs)
    stats.total_crawling_sessions = len(investigation.crawling_sessions)
    stats.total_reports = len(investigation.reports)
    stats.total_findings = len(investigation.findings)

    # Count critical and high findings
    for finding in investigation.findings:
        if finding.severity == FindingSeverity.CRITICAL:
            stats.critical_findings += 1
        elif finding.severity == FindingSeverity.HIGH:
            stats.high_findings += 1

    return stats


@router.patch("/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(
    investigation_id: int,
    investigation_data: InvestigationUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update investigation"""
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    # Update investigation
    for field, value in investigation_data.model_dump(exclude_unset=True).items():
        setattr(investigation, field, value)

    await db.commit()
    await db.refresh(investigation)

    return investigation


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Delete investigation"""
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    await db.delete(investigation)
    await db.commit()

    return None
