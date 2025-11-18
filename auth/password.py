"""Password hashing and verification."""

from passlib.context import CryptContext
from loguru import logger


class PasswordHasher:
    """
    Password hashing using bcrypt.

    Features:
    - Secure password hashing
    - Password verification
    - Configurable rounds
    - Automatic rehashing for security
    """

    def __init__(self, schemes: list = None, deprecated: str = None):
        """
        Initialize password hasher.

        Args:
            schemes: List of hashing schemes (default: bcrypt)
            deprecated: Deprecated schemes
        """
        self.pwd_context = CryptContext(
            schemes=schemes or ["bcrypt"],
            deprecated=deprecated or "auto",
        )

        logger.info("Password hasher initialized")

    def hash_password(self, password: str) -> str:
        """
        Hash a password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if password hash needs updating.

        Args:
            hashed_password: Hashed password

        Returns:
            True if rehash needed, False otherwise
        """
        return self.pwd_context.needs_update(hashed_password)
