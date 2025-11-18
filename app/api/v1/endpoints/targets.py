"""Target endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst, get_pagination_params
from app.models.user import User
from app.models.target import Target
from app.models.investigation import Investigation
from app.schemas.target import TargetCreate, TargetUpdate, TargetResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Create a new target"""
    # Verify investigation exists
    result = await db.execute(
        select(Investigation).where(Investigation.id == target_data.investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    new_target = Target(**target_data.model_dump())

    db.add(new_target)
    await db.commit()
    await db.refresh(new_target)

    return new_target


@router.get("/", response_model=PaginatedResponse[TargetResponse])
async def list_targets(
    investigation_id: Optional[int] = Query(None),
    type_filter: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List targets with filtering"""
    query = select(Target)

    # Apply filters
    if investigation_id:
        query = query.where(Target.investigation_id == investigation_id)
    if type_filter:
        query = query.where(Target.type == type_filter)
    if status_filter:
        query = query.where(Target.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(pagination["offset"]).limit(pagination["page_size"])
    result = await db.execute(query)
    targets = result.scalars().all()

    return {
        "items": targets,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get target by ID"""
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )

    return target


@router.patch("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: int,
    target_data: TargetUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update target"""
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )

    # Update target
    for field, value in target_data.model_dump(exclude_unset=True).items():
        setattr(target, field, value)

    await db.commit()
    await db.refresh(target)

    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Delete target"""
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )

    await db.delete(target)
    await db.commit()

    return None
