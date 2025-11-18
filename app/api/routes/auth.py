"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db, User
from app.security import password_handler, create_access_token, create_refresh_token, verify_token
from app.auth.oauth2 import oauth2_handler
from app.auth.dependencies import get_current_active_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""

    # Validate password strength
    is_valid, error_msg = password_handler.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=password_handler.hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_verified=not settings.REQUIRE_EMAIL_VERIFICATION
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with email/username and password"""

    # Find user by email or username
    result = await db.execute(
        select(User).where(
            (User.email == form_data.username) | (User.username == form_data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not password_handler.verify_password(form_data.password, user.hashed_password):
        # Increment failed login attempts
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES
                )
            await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to multiple failed login attempts"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""

    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/oauth2/{provider}/authorize")
async def oauth2_authorize(provider: str, redirect_uri: str):
    """Get OAuth2 authorization URL"""
    try:
        auth_url = oauth2_handler.get_authorization_url(provider, redirect_uri)
        return {"authorization_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/oauth2/{provider}/callback", response_model=TokenResponse)
async def oauth2_callback(
    provider: str,
    code: str,
    redirect_uri: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth2 callback and create/login user"""

    # Exchange code for token
    access_token = await oauth2_handler.exchange_code_for_token(provider, code, redirect_uri)

    # Get user info from provider
    if provider == "google":
        user_info = await oauth2_handler.get_google_user_info(access_token)
    elif provider == "github":
        user_info = await oauth2_handler.get_github_user_info(access_token)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to get user info from OAuth2 provider"
        )

    # Find or create user
    email = user_info.get("email")
    oauth_id = str(user_info.get("id"))

    result = await db.execute(
        select(User).where(
            (User.email == email) |
            ((User.oauth_provider == provider) & (User.oauth_id == oauth_id))
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        username = user_info.get("login") or user_info.get("email").split("@")[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            email=email,
            username=username,
            hashed_password="oauth2",  # No password for OAuth2 users
            full_name=user_info.get("name"),
            oauth_provider=provider,
            oauth_id=oauth_id,
            is_active=True,
            is_verified=True  # OAuth2 users are pre-verified
        )
        db.add(user)
    else:
        # Update OAuth2 info if needed
        if not user.oauth_provider:
            user.oauth_provider = provider
            user.oauth_id = oauth_id

        user.last_login_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    # Create tokens
    jwt_access_token = create_access_token(data={"sub": str(user.id)})
    jwt_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": jwt_access_token,
        "refresh_token": jwt_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
