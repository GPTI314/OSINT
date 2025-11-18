"""Role-Based Access Control (RBAC) system."""

from typing import List, Set
from enum import Enum
from loguru import logger


class Permission(Enum):
    """System permissions."""
    # Investigation permissions
    INVESTIGATION_CREATE = "investigation:create"
    INVESTIGATION_READ = "investigation:read"
    INVESTIGATION_UPDATE = "investigation:update"
    INVESTIGATION_DELETE = "investigation:delete"

    # Target permissions
    TARGET_CREATE = "target:create"
    TARGET_READ = "target:read"
    TARGET_UPDATE = "target:update"
    TARGET_DELETE = "target:delete"

    # Scraping permissions
    SCRAPING_CREATE = "scraping:create"
    SCRAPING_READ = "scraping:read"
    SCRAPING_STOP = "scraping:stop"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # System administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_METRICS = "system:metrics"


class Role(Enum):
    """User roles."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Role permission mappings
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        # Full access to everything
        Permission.INVESTIGATION_CREATE,
        Permission.INVESTIGATION_READ,
        Permission.INVESTIGATION_UPDATE,
        Permission.INVESTIGATION_DELETE,
        Permission.TARGET_CREATE,
        Permission.TARGET_READ,
        Permission.TARGET_UPDATE,
        Permission.TARGET_DELETE,
        Permission.SCRAPING_CREATE,
        Permission.SCRAPING_READ,
        Permission.SCRAPING_STOP,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_LOGS,
        Permission.SYSTEM_METRICS,
    },
    Role.ANALYST: {
        # Can manage investigations and targets
        Permission.INVESTIGATION_CREATE,
        Permission.INVESTIGATION_READ,
        Permission.INVESTIGATION_UPDATE,
        Permission.TARGET_CREATE,
        Permission.TARGET_READ,
        Permission.TARGET_UPDATE,
        Permission.SCRAPING_CREATE,
        Permission.SCRAPING_READ,
        Permission.SCRAPING_STOP,
        Permission.USER_READ,
    },
    Role.VIEWER: {
        # Read-only access
        Permission.INVESTIGATION_READ,
        Permission.TARGET_READ,
        Permission.SCRAPING_READ,
    },
}


class RBACManager:
    """Role-Based Access Control manager."""

    def __init__(self):
        """Initialize RBAC manager."""
        logger.info("RBAC manager initialized")

    def has_permission(self, role: str, permission: Permission) -> bool:
        """
        Check if role has specific permission.

        Args:
            role: User role
            permission: Permission to check

        Returns:
            True if role has permission, False otherwise
        """
        try:
            role_enum = Role(role)
            permissions = ROLE_PERMISSIONS.get(role_enum, set())
            return permission in permissions
        except (ValueError, KeyError):
            logger.warning(f"Invalid role: {role}")
            return False

    def get_role_permissions(self, role: str) -> Set[Permission]:
        """
        Get all permissions for a role.

        Args:
            role: User role

        Returns:
            Set of permissions
        """
        try:
            role_enum = Role(role)
            return ROLE_PERMISSIONS.get(role_enum, set())
        except (ValueError, KeyError):
            logger.warning(f"Invalid role: {role}")
            return set()

    def can_access_resource(
        self,
        role: str,
        resource_type: str,
        action: str,
    ) -> bool:
        """
        Check if role can perform action on resource type.

        Args:
            role: User role
            resource_type: Type of resource
            action: Action to perform

        Returns:
            True if allowed, False otherwise
        """
        try:
            permission_str = f"{resource_type}:{action}"
            permission = Permission(permission_str)
            return self.has_permission(role, permission)
        except (ValueError, KeyError):
            return False

    def is_admin(self, role: str) -> bool:
        """Check if role is admin."""
        return role == Role.ADMIN.value

    def is_analyst(self, role: str) -> bool:
        """Check if role is analyst or higher."""
        return role in [Role.ADMIN.value, Role.ANALYST.value]
