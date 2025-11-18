"""Crawling Session endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst, get_pagination_params
from app.models.user import User
from app.models.crawling import CrawlingSession
from app.models.investigation import Investigation
from app.schemas.crawling import CrawlingSessionCreate, CrawlingSessionUpdate, CrawlingSessionResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=CrawlingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_crawling_session(
    session_data: CrawlingSessionCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Create a new crawling session"""
    # Verify investigation exists
    result = await db.execute(
        select(Investigation).where(Investigation.id == session_data.investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    new_session = CrawlingSession(**session_data.model_dump())

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


@router.get("/", response_model=PaginatedResponse[CrawlingSessionResponse])
async def list_crawling_sessions(
    investigation_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List crawling sessions with filtering"""
    query = select(CrawlingSession)

    # Apply filters
    if investigation_id:
        query = query.where(CrawlingSession.investigation_id == investigation_id)
    if status_filter:
        query = query.where(CrawlingSession.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(pagination["offset"]).limit(pagination["page_size"])
    result = await db.execute(query)
    sessions = result.scalars().all()

    return {
        "items": sessions,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{session_id}", response_model=CrawlingSessionResponse)
async def get_crawling_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get crawling session by ID"""
    result = await db.execute(select(CrawlingSession).where(CrawlingSession.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawling session not found",
        )

    return session


@router.patch("/{session_id}", response_model=CrawlingSessionResponse)
async def update_crawling_session(
    session_id: int,
    session_data: CrawlingSessionUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update crawling session"""
    result = await db.execute(select(CrawlingSession).where(CrawlingSession.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawling session not found",
        )

    # Update session
    for field, value in session_data.model_dump(exclude_unset=True).items():
        setattr(session, field, value)

    await db.commit()
    await db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crawling_session(
    session_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Delete crawling session"""
    result = await db.execute(select(CrawlingSession).where(CrawlingSession.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawling session not found",
        )

    await db.delete(session)
    await db.commit()

    return None


@router.post("/{session_id}/start", response_model=CrawlingSessionResponse)
async def start_crawling_session(
    session_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Start a crawling session"""
    result = await db.execute(select(CrawlingSession).where(CrawlingSession.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawling session not found",
        )

    from app.models.crawling import CrawlingSessionStatus
    from datetime import datetime

    session.status = CrawlingSessionStatus.RUNNING
    session.started_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    # TODO: Trigger actual crawling task via Celery

    return session


@router.post("/{session_id}/stop", response_model=CrawlingSessionResponse)
async def stop_crawling_session(
    session_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Stop a crawling session"""
    result = await db.execute(select(CrawlingSession).where(CrawlingSession.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawling session not found",
        )

    from app.models.crawling import CrawlingSessionStatus

    session.status = CrawlingSessionStatus.PAUSED

    await db.commit()
    await db.refresh(session)

    # TODO: Cancel crawling task via Celery

    return session
