"""API Key endpoints"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.core.security import generate_api_key, hash_api_key
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse, APIKeyUpdate

router = APIRouter()


@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key"""
    # Generate API key
    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)
    prefix = plain_key[:8]

    # Calculate expiration
    expires_at = None
    if api_key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)

    # Create API key
    new_api_key = APIKey(
        name=api_key_data.name,
        key_hash=key_hash,
        prefix=prefix,
        user_id=current_user.id,
        expires_at=expires_at,
        scopes=",".join(api_key_data.scopes) if api_key_data.scopes else None
    )

    db.add(new_api_key)
    await db.commit()
    await db.refresh(new_api_key)

    # Return response with full key (only time it's shown)
    response = APIKeyCreateResponse(
        id=new_api_key.id,
        name=new_api_key.name,
        prefix=new_api_key.prefix,
        is_active=new_api_key.is_active,
        created_at=new_api_key.created_at,
        expires_at=new_api_key.expires_at,
        last_used_at=new_api_key.last_used_at,
        user_id=new_api_key.user_id,
        scopes=api_key_data.scopes,
        key=plain_key
    )

    return response


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's API keys"""
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == current_user.id)
    )
    api_keys = result.scalars().all()

    return api_keys


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get API key details"""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return api_key


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: int,
    api_key_data: APIKeyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update API key"""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    # Update API key
    for field, value in api_key_data.model_dump(exclude_unset=True).items():
        if field == "scopes" and value is not None:
            setattr(api_key, field, ",".join(value))
        else:
            setattr(api_key, field, value)

    await db.commit()
    await db.refresh(api_key)

    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete API key"""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await db.delete(api_key)
    await db.commit()

    return None
