"""User endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_admin, get_pagination_params
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import PaginatedResponse
from app.core.rate_limit import limiter
from fastapi import Request

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information"""
    # Users can't change their own role
    if user_data.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role",
        )

    # Update user
    for field, value in user_data.model_dump(exclude_unset=True).items():
        if field != "role":  # Ensure role is not changed
            setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/", response_model=PaginatedResponse[UserResponse])
@limiter.limit("30/minute")
async def list_users(
    request: Request,
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)"""
    # Get total count
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar_one()

    # Get paginated users
    result = await db.execute(
        select(User)
        .offset(pagination["offset"])
        .limit(pagination["page_size"])
    )
    users = result.scalars().all()

    return {
        "items": users,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update user
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()

    return None
