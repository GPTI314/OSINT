"""Scraping Job endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst, get_pagination_params
from app.models.user import User
from app.models.scraping import ScrapingJob
from app.models.investigation import Investigation
from app.schemas.scraping import ScrapingJobCreate, ScrapingJobUpdate, ScrapingJobResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=ScrapingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_scraping_job(
    job_data: ScrapingJobCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Create a new scraping job"""
    # Verify investigation exists
    result = await db.execute(
        select(Investigation).where(Investigation.id == job_data.investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    new_job = ScrapingJob(**job_data.model_dump())

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    return new_job


@router.get("/", response_model=PaginatedResponse[ScrapingJobResponse])
async def list_scraping_jobs(
    investigation_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    type_filter: Optional[str] = Query(None, alias="type"),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List scraping jobs with filtering"""
    query = select(ScrapingJob)

    # Apply filters
    if investigation_id:
        query = query.where(ScrapingJob.investigation_id == investigation_id)
    if status_filter:
        query = query.where(ScrapingJob.status == status_filter)
    if type_filter:
        query = query.where(ScrapingJob.type == type_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(pagination["offset"]).limit(pagination["page_size"])
    result = await db.execute(query)
    jobs = result.scalars().all()

    return {
        "items": jobs,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{job_id}", response_model=ScrapingJobResponse)
async def get_scraping_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get scraping job by ID"""
    result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    return job


@router.patch("/{job_id}", response_model=ScrapingJobResponse)
async def update_scraping_job(
    job_id: int,
    job_data: ScrapingJobUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update scraping job"""
    result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    # Update job
    for field, value in job_data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)

    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scraping_job(
    job_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Delete scraping job"""
    result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    await db.delete(job)
    await db.commit()

    return None


@router.post("/{job_id}/start", response_model=ScrapingJobResponse)
async def start_scraping_job(
    job_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Start a scraping job"""
    result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    from app.models.scraping import ScrapingJobStatus
    from datetime import datetime

    job.status = ScrapingJobStatus.RUNNING
    job.started_at = datetime.utcnow()

    await db.commit()
    await db.refresh(job)

    # TODO: Trigger actual scraping task via Celery

    return job


@router.post("/{job_id}/stop", response_model=ScrapingJobResponse)
async def stop_scraping_job(
    job_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Stop a scraping job"""
    result = await db.execute(select(ScrapingJob).where(ScrapingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    from app.models.scraping import ScrapingJobStatus

    job.status = ScrapingJobStatus.PAUSED

    await db.commit()
    await db.refresh(job)

    # TODO: Cancel scraping task via Celery

    return job
