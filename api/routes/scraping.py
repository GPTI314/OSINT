"""Scraping job routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.connection import get_db
from database.models import ScrapingJob, JobStatus, Target, User
from auth.authenticator import Authenticator
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
authenticator = Authenticator()


class ScrapingJobCreate(BaseModel):
    """Scraping job creation schema."""
    target_id: int
    url: str
    scraper_type: str = "static"
    config: Optional[Dict[str, Any]] = None


class ScrapingJobResponse(BaseModel):
    """Scraping job response schema."""
    id: int
    target_id: int
    url: str
    scraper_type: str
    status: str
    progress: float
    items_scraped: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get current user."""
    user = await authenticator.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@router.post("/", response_model=ScrapingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_scraping_job(
    job_data: ScrapingJobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new scraping job."""
    # Verify target exists
    result = await db.execute(
        select(Target).where(Target.id == job_data.target_id)
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )

    # Create job
    job = ScrapingJob(
        target_id=job_data.target_id,
        url=job_data.url,
        scraper_type=job_data.scraper_type,
        status=JobStatus.PENDING,
        config=job_data.config or {},
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Schedule scraping task
    # background_tasks.add_task(run_scraping_job, job.id)

    return job


@router.get("/", response_model=List[ScrapingJobResponse])
async def list_scraping_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    target_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List scraping jobs."""
    query = select(ScrapingJob)

    if status:
        try:
            job_status = JobStatus(status)
            query = query.where(ScrapingJob.status == job_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}",
            )

    if target_id:
        query = query.where(ScrapingJob.target_id == target_id)

    query = query.offset(skip).limit(limit).order_by(ScrapingJob.created_at.desc())

    result = await db.execute(query)
    jobs = result.scalars().all()

    return jobs


@router.get("/{job_id}", response_model=ScrapingJobResponse)
async def get_scraping_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scraping job by ID."""
    result = await db.execute(
        select(ScrapingJob).where(ScrapingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    return job


@router.post("/{job_id}/cancel", response_model=ScrapingJobResponse)
async def cancel_scraping_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a scraping job."""
    result = await db.execute(
        select(ScrapingJob).where(ScrapingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scraping job not found",
        )

    if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status.value}",
        )

    job.status = JobStatus.CANCELLED
    await db.commit()
    await db.refresh(job)

    return job
