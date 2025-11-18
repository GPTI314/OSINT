"""
Password hashing and validation using Argon2 and bcrypt
"""
from passlib.context import CryptContext
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import re
from typing import Tuple
from app.config import settings


class PasswordHandler:
    """Secure password hashing and validation"""

    def __init__(self):
        # Use Argon2 as primary (winner of Password Hashing Competition)
        # Bcrypt as fallback for compatibility
        self.pwd_context = CryptContext(
            schemes=["argon2", "bcrypt"],
            deprecated="auto",
            argon2__memory_cost=65536,  # 64 MB
            argon2__time_cost=3,
            argon2__parallelism=4,
        )
        self.argon2 = PasswordHasher(
            memory_cost=65536,
            time_cost=3,
            parallelism=4
        )

    def hash_password(self, password: str) -> str:
        """Hash password using Argon2"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if password hash needs updating"""
        return self.pwd_context.needs_update(hashed_password)

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password against security policy
        Returns: (is_valid, error_message)
        """
        errors = []

        # Length check
        if len(password) < settings.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters")

        # Uppercase check
        if settings.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        # Lowercase check
        if settings.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        # Digit check
        if settings.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        # Special character check
        if settings.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        # Common password check
        if self._is_common_password(password):
            errors.append("Password is too common. Please choose a stronger password")

        if errors:
            return False, "; ".join(errors)

        return True, ""

    def _is_common_password(self, password: str) -> bool:
        """Check against common passwords"""
        common_passwords = {
            'password', 'password123', '12345678', 'qwerty', 'abc123',
            'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
            'baseball', 'iloveyou', 'master', 'sunshine', 'ashley',
            'bailey', 'passw0rd', 'shadow', '123123', '654321'
        }
        return password.lower() in common_passwords


# Global password handler instance
password_handler = PasswordHandler()
