"""User authentication logic."""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from database.models import User
from .password import PasswordHasher
from .jwt_manager import JWTManager


class Authenticator:
    """
    User authentication handler.

    Features:
    - Email/password authentication
    - JWT token generation
    - User validation
    - Session management
    """

    def __init__(self):
        """Initialize authenticator."""
        self.password_hasher = PasswordHasher()
        self.jwt_manager = JWTManager()

        logger.info("Authenticator initialized")

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password.

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            Authentication result with tokens or None
        """
        try:
            # Get user by email
            result = await db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"Authentication failed: user not found ({email})")
                return None

            # Verify password
            if not self.password_hasher.verify_password(
                password,
                user.hashed_password
            ):
                logger.warning(f"Authentication failed: invalid password ({email})")
                return None

            # Check if user is active
            if not user.is_active:
                logger.warning(f"Authentication failed: user inactive ({email})")
                return None

            # Update last login
            user.last_login = datetime.utcnow()
            await db.commit()

            # Generate tokens
            tokens = self.jwt_manager.create_token_pair(
                subject=str(user.id),
                additional_claims={
                    "email": user.email,
                    "role": user.role.value,
                }
            )

            logger.info(f"User authenticated successfully: {email}")

            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                },
                **tokens
            }

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def get_current_user(
        self,
        db: AsyncSession,
        token: str,
    ) -> Optional[User]:
        """
        Get current user from JWT token.

        Args:
            db: Database session
            token: JWT access token

        Returns:
            User object or None
        """
        try:
            # Decode token
            payload = self.jwt_manager.decode_token(token)
            if not payload:
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            # Get user from database
            result = await db.execute(
                select(User).where(User.id == int(user_id))
            )
            user = result.scalar_one_or_none()

            if not user or not user.is_active:
                return None

            return user

        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> Optional[Dict[str, str]]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            New tokens or None
        """
        try:
            # Verify refresh token
            if not self.jwt_manager.verify_token(refresh_token, token_type="refresh"):
                return None

            # Decode token to get user info
            payload = self.jwt_manager.decode_token(refresh_token)
            if not payload:
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            # Generate new token pair
            tokens = self.jwt_manager.create_token_pair(subject=user_id)

            logger.info(f"Access token refreshed for user: {user_id}")
            return tokens

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    async def register_user(
        self,
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> Optional[User]:
        """
        Register a new user.

        Args:
            db: Database session
            email: User email
            username: Username
            password: Password
            full_name: Full name (optional)

        Returns:
            Created user or None
        """
        try:
            # Check if user exists
            result = await db.execute(
                select(User).where(
                    (User.email == email) | (User.username == username)
                )
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.warning(f"User already exists: {email} or {username}")
                return None

            # Hash password
            hashed_password = self.password_hasher.hash_password(password)

            # Create user
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False,
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            logger.info(f"User registered successfully: {email}")
            return user

        except Exception as e:
            logger.error(f"Error registering user: {e}")
            await db.rollback()
            return None
