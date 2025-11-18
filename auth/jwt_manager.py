"""JWT token management for authentication."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from loguru import logger
from config.settings import settings


class JWTManager:
    """
    JWT token manager for creating and validating tokens.

    Features:
    - Access token generation
    - Refresh token generation
    - Token validation
    - Token expiration
    - Claims management
    """

    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = None,
        access_token_expire_minutes: int = None,
        refresh_token_expire_days: int = None,
    ):
        """
        Initialize JWT manager.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm or settings.jwt_algorithm
        self.access_token_expire_minutes = (
            access_token_expire_minutes or settings.access_token_expire_minutes
        )
        self.refresh_token_expire_days = (
            refresh_token_expire_days or settings.refresh_token_expire_days
        )

        logger.info("JWT manager initialized")

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT access token.

        Args:
            data: Data to encode in token
            expires_delta: Optional custom expiration delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            data: Data to encode in token
            expires_delta: Optional custom expiration delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=self.refresh_token_expire_days
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload

        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def verify_token(self, token: str, token_type: str = "access") -> bool:
        """
        Verify JWT token validity.

        Args:
            token: JWT token to verify
            token_type: Expected token type (access or refresh)

        Returns:
            True if valid, False otherwise
        """
        payload = self.decode_token(token)

        if not payload:
            return False

        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}")
            return False

        return True

    def get_token_subject(self, token: str) -> Optional[str]:
        """
        Extract subject from token.

        Args:
            token: JWT token

        Returns:
            Subject from token or None
        """
        payload = self.decode_token(token)
        return payload.get("sub") if payload else None

    def create_token_pair(
        self,
        subject: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Create both access and refresh tokens.

        Args:
            subject: Token subject (usually user ID)
            additional_claims: Additional claims to include

        Returns:
            Dictionary with access_token and refresh_token
        """
        claims = {"sub": subject}
        if additional_claims:
            claims.update(additional_claims)

        access_token = self.create_access_token(claims)
        refresh_token = self.create_refresh_token({"sub": subject})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
