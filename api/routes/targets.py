"""Target management routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from database.models import Target, TargetType, User
from auth.authenticator import Authenticator
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
authenticator = Authenticator()


class TargetCreate(BaseModel):
    """Target creation schema."""
    type: str
    value: str
    name: Optional[str] = None
    description: Optional[str] = None


class TargetResponse(BaseModel):
    """Target response schema."""
    id: int
    type: str
    value: str
    name: Optional[str]
    description: Optional[str]
    risk_score: float
    created_at: datetime
    updated_at: datetime

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


@router.post("/", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new target."""
    try:
        target_type = TargetType(target_data.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target type: {target_data.type}",
        )

    target = Target(
        type=target_type,
        value=target_data.value,
        name=target_data.name,
        description=target_data.description,
    )

    db.add(target)
    await db.commit()
    await db.refresh(target)

    return target


@router.get("/", response_model=List[TargetResponse])
async def list_targets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List targets."""
    query = select(Target)

    if type:
        try:
            target_type = TargetType(type)
            query = query.where(Target.type == target_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid target type: {type}",
            )

    query = query.offset(skip).limit(limit).order_by(Target.created_at.desc())

    result = await db.execute(query)
    targets = result.scalars().all()

    return targets


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get target by ID."""
    result = await db.execute(
        select(Target).where(Target.id == target_id)
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )

    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete target."""
    result = await db.execute(
        select(Target).where(Target.id == target_id)
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )

    await db.delete(target)
    await db.commit()

    return None
