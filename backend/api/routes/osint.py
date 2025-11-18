"""
OSINT investigation endpoints for intelligence gathering operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.database import get_db
from models.user import User
from models.investigation import Investigation, InvestigationStatus
from models.target import Target, TargetType
from models.result import OSINTResult, ResultType
from api.routes.auth import get_current_user

router = APIRouter()


# Pydantic schemas
class InvestigationCreate(BaseModel):
    """Investigation creation schema."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    tags: List[str] = Field(default_factory=list)


class InvestigationResponse(BaseModel):
    """Investigation response schema."""
    id: int
    title: str
    description: Optional[str]
    status: InvestigationStatus
    created_by: int
    priority: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TargetCreate(BaseModel):
    """Target creation schema."""
    target_type: TargetType
    value: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None


class TargetResponse(BaseModel):
    """Target response schema."""
    id: int
    investigation_id: int
    target_type: TargetType
    value: str
    description: Optional[str]
    risk_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class OSINTRequest(BaseModel):
    """OSINT operation request schema."""
    target_type: TargetType
    target_value: str
    operations: List[str] = Field(
        default_factory=lambda: ["whois", "dns", "geolocation"],
        description="List of OSINT operations to perform"
    )


# Investigation endpoints
@router.post("/investigations", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation_data: InvestigationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new OSINT investigation.

    Args:
        investigation_data: Investigation creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        InvestigationResponse: Created investigation
    """
    investigation = Investigation(
        title=investigation_data.title,
        description=investigation_data.description,
        created_by=current_user.id,
        priority=investigation_data.priority,
        tags=investigation_data.tags
    )

    db.add(investigation)
    await db.commit()
    await db.refresh(investigation)

    return investigation


@router.get("/investigations", response_model=List[InvestigationResponse])
async def list_investigations(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[InvestigationStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all investigations for the current user.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Optional status filter
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[InvestigationResponse]: List of investigations
    """
    query = select(Investigation).where(Investigation.created_by == current_user.id)

    if status_filter:
        query = query.where(Investigation.status == status_filter)

    query = query.offset(skip).limit(limit).order_by(Investigation.created_at.desc())

    result = await db.execute(query)
    investigations = result.scalars().all()

    return investigations


@router.get("/investigations/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get investigation by ID.

    Args:
        investigation_id: Investigation ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        InvestigationResponse: Investigation data
    """
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.created_by == current_user.id
        )
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found"
        )

    return investigation


@router.patch("/investigations/{investigation_id}/status")
async def update_investigation_status(
    investigation_id: int,
    new_status: InvestigationStatus,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update investigation status.

    Args:
        investigation_id: Investigation ID
        new_status: New status
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Updated investigation
    """
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.created_by == current_user.id
        )
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found"
        )

    investigation.status = new_status

    if new_status == InvestigationStatus.ACTIVE and not investigation.started_at:
        investigation.started_at = datetime.utcnow()
    elif new_status == InvestigationStatus.COMPLETED:
        investigation.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(investigation)

    return investigation


# Target endpoints
@router.post("/investigations/{investigation_id}/targets", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def add_target(
    investigation_id: int,
    target_data: TargetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a target to an investigation.

    Args:
        investigation_id: Investigation ID
        target_data: Target creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        TargetResponse: Created target
    """
    # Verify investigation exists and belongs to user
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.created_by == current_user.id
        )
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found"
        )

    target = Target(
        investigation_id=investigation_id,
        target_type=target_data.target_type,
        value=target_data.value,
        description=target_data.description
    )

    db.add(target)
    await db.commit()
    await db.refresh(target)

    return target


@router.get("/investigations/{investigation_id}/targets", response_model=List[TargetResponse])
async def list_targets(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all targets for an investigation.

    Args:
        investigation_id: Investigation ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[TargetResponse]: List of targets
    """
    # Verify investigation exists and belongs to user
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.created_by == current_user.id
        )
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found"
        )

    result = await db.execute(
        select(Target).where(Target.investigation_id == investigation_id)
    )
    targets = result.scalars().all()

    return targets


@router.post("/investigate")
async def quick_investigate(
    osint_request: OSINTRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Perform quick OSINT investigation on a target.

    This endpoint triggers background tasks to perform various OSINT operations
    on the specified target.

    Args:
        osint_request: OSINT request data
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user

    Returns:
        dict: Investigation task ID and status
    """
    # This will be implemented with Celery tasks
    task_id = f"task_{datetime.utcnow().timestamp()}"

    return {
        "task_id": task_id,
        "status": "queued",
        "target_type": osint_request.target_type,
        "target_value": osint_request.target_value,
        "operations": osint_request.operations,
        "message": "OSINT investigation queued for processing"
    }
