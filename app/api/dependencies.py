"""API dependencies for authentication and authorization"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token, verify_api_key
from app.models.user import User, UserRole
from app.models.api_key import APIKey

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_user_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user from API key"""
    if not x_api_key:
        return None

    # Extract prefix (first 8 chars)
    prefix = x_api_key[:8]

    # Find API key by prefix
    result = await db.execute(
        select(APIKey).where(APIKey.prefix == prefix, APIKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        return None

    # Verify the full API key
    if not verify_api_key(x_api_key, api_key.key_hash):
        return None

    # Check if expired
    from datetime import datetime
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return None

    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    # Get user
    result = await db.execute(select(User).where(User.id == api_key.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None

    return user


async def get_current_active_user(
    user: Optional[User] = Depends(get_current_user),
    api_key_user: Optional[User] = Depends(get_current_user_from_api_key),
) -> User:
    """Get current active user (from JWT or API key)"""
    current_user = user or api_key_user

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def require_analyst(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require analyst role or higher"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ANALYST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst privileges required",
        )
    return current_user


def get_pagination_params(page: int = 1, page_size: int = 20):
    """Get pagination parameters"""
    from app.core.config import settings

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = settings.DEFAULT_PAGE_SIZE
    if page_size > settings.MAX_PAGE_SIZE:
        page_size = settings.MAX_PAGE_SIZE

    return {"page": page, "page_size": page_size, "offset": (page - 1) * page_size}
