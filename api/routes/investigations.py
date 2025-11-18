"""Investigation management routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from database.models import Investigation, InvestigationStatus, User
from auth.authenticator import Authenticator
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
authenticator = Authenticator()


class InvestigationCreate(BaseModel):
    """Investigation creation schema."""
    name: str
    description: Optional[str] = None
    priority: int = 0


class InvestigationUpdate(BaseModel):
    """Investigation update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None


class InvestigationResponse(BaseModel):
    """Investigation response schema."""
    id: int
    name: str
    description: Optional[str]
    status: str
    priority: int
    created_by: int
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


@router.post("/", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation_data: InvestigationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new investigation."""
    investigation = Investigation(
        name=investigation_data.name,
        description=investigation_data.description,
        priority=investigation_data.priority,
        status=InvestigationStatus.DRAFT,
        created_by=current_user.id,
    )

    db.add(investigation)
    await db.commit()
    await db.refresh(investigation)

    return investigation


@router.get("/", response_model=List[InvestigationResponse])
async def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List investigations."""
    query = select(Investigation)

    if status:
        query = query.where(Investigation.status == InvestigationStatus(status))

    query = query.offset(skip).limit(limit).order_by(Investigation.created_at.desc())

    result = await db.execute(query)
    investigations = result.scalars().all()

    return investigations


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get investigation by ID."""
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


@router.patch("/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(
    investigation_id: int,
    investigation_data: InvestigationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update investigation."""
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    # Update fields
    if investigation_data.name is not None:
        investigation.name = investigation_data.name
    if investigation_data.description is not None:
        investigation.description = investigation_data.description
    if investigation_data.status is not None:
        investigation.status = InvestigationStatus(investigation_data.status)
    if investigation_data.priority is not None:
        investigation.priority = investigation_data.priority

    await db.commit()
    await db.refresh(investigation)

    return investigation


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete investigation."""
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
