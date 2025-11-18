"""
Role-Based Access Control (RBAC) implementation
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.models import User, Role, Permission


class RBACManager:
    """Manage roles and permissions"""

    @staticmethod
    async def create_role(
        db: AsyncSession,
        name: str,
        description: str = "",
        is_system: bool = False
    ) -> Role:
        """Create a new role"""
        role = Role(
            name=name,
            description=description,
            is_system=is_system
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def create_permission(
        db: AsyncSession,
        name: str,
        resource: str,
        action: str,
        description: str = ""
    ) -> Permission:
        """Create a new permission"""
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission

    @staticmethod
    async def assign_permission_to_role(
        db: AsyncSession,
        role: Role,
        permission: Permission
    ):
        """Assign a permission to a role"""
        if permission not in role.permissions:
            role.permissions.append(permission)
            await db.commit()

    @staticmethod
    async def assign_role_to_user(
        db: AsyncSession,
        user: User,
        role: Role
    ):
        """Assign a role to a user"""
        if role not in user.roles:
            user.roles.append(role)
            await db.commit()

    @staticmethod
    async def remove_role_from_user(
        db: AsyncSession,
        user: User,
        role: Role
    ):
        """Remove a role from a user"""
        if role in user.roles:
            user.roles.remove(role)
            await db.commit()

    @staticmethod
    async def get_user_permissions(
        db: AsyncSession,
        user: User
    ) -> List[Permission]:
        """Get all permissions for a user through their roles"""
        # Refresh user with roles and permissions
        await db.refresh(user, ['roles'])

        permissions = []
        for role in user.roles:
            await db.refresh(role, ['permissions'])
            permissions.extend(role.permissions)

        # Remove duplicates
        unique_permissions = list({p.id: p for p in permissions}.values())
        return unique_permissions


async def check_permission(
    user: User,
    permission_name: str,
    db: AsyncSession
) -> bool:
    """Check if user has a specific permission"""
    # Superusers have all permissions
    if user.is_superuser:
        return True

    # Get user permissions
    permissions = await RBACManager.get_user_permissions(db, user)

    # Check if permission exists
    return any(p.name == permission_name for p in permissions)


async def has_role(
    user: User,
    role_name: str,
    db: AsyncSession
) -> bool:
    """Check if user has a specific role"""
    await db.refresh(user, ['roles'])
    return any(r.name == role_name for r in user.roles)


async def initialize_rbac(db: AsyncSession):
    """Initialize default roles and permissions"""
    # Create default roles
    roles_data = [
        {
            'name': 'admin',
            'description': 'System administrator with full access',
            'is_system': True
        },
        {
            'name': 'analyst',
            'description': 'OSINT analyst with investigation capabilities',
            'is_system': True
        },
        {
            'name': 'viewer',
            'description': 'Read-only access to reports and data',
            'is_system': True
        },
        {
            'name': 'api_user',
            'description': 'Programmatic API access',
            'is_system': True
        }
    ]

    roles = {}
    for role_data in roles_data:
        # Check if role exists
        result = await db.execute(
            select(Role).where(Role.name == role_data['name'])
        )
        role = result.scalar_one_or_none()

        if not role:
            role = await RBACManager.create_role(db, **role_data)

        roles[role.name] = role

    # Create default permissions
    permissions_data = [
        # User management
        {'name': 'user:create', 'resource': 'user', 'action': 'create', 'description': 'Create users'},
        {'name': 'user:read', 'resource': 'user', 'action': 'read', 'description': 'View users'},
        {'name': 'user:update', 'resource': 'user', 'action': 'update', 'description': 'Update users'},
        {'name': 'user:delete', 'resource': 'user', 'action': 'delete', 'description': 'Delete users'},

        # Investigation
        {'name': 'investigation:create', 'resource': 'investigation', 'action': 'create', 'description': 'Create investigations'},
        {'name': 'investigation:read', 'resource': 'investigation', 'action': 'read', 'description': 'View investigations'},
        {'name': 'investigation:update', 'resource': 'investigation', 'action': 'update', 'description': 'Update investigations'},
        {'name': 'investigation:delete', 'resource': 'investigation', 'action': 'delete', 'description': 'Delete investigations'},

        # Data collection
        {'name': 'collector:execute', 'resource': 'collector', 'action': 'execute', 'description': 'Run OSINT collectors'},
        {'name': 'collector:configure', 'resource': 'collector', 'action': 'configure', 'description': 'Configure collectors'},

        # Reports
        {'name': 'report:create', 'resource': 'report', 'action': 'create', 'description': 'Generate reports'},
        {'name': 'report:read', 'resource': 'report', 'action': 'read', 'description': 'View reports'},
        {'name': 'report:export', 'resource': 'report', 'action': 'export', 'description': 'Export reports'},

        # System
        {'name': 'system:admin', 'resource': 'system', 'action': 'admin', 'description': 'System administration'},
        {'name': 'audit:read', 'resource': 'audit', 'action': 'read', 'description': 'View audit logs'},
    ]

    permissions = {}
    for perm_data in permissions_data:
        # Check if permission exists
        result = await db.execute(
            select(Permission).where(Permission.name == perm_data['name'])
        )
        permission = result.scalar_one_or_none()

        if not permission:
            permission = await RBACManager.create_permission(db, **perm_data)

        permissions[permission.name] = permission

    # Assign permissions to roles
    # Admin: all permissions
    for permission in permissions.values():
        await RBACManager.assign_permission_to_role(db, roles['admin'], permission)

    # Analyst: investigation and collection permissions
    analyst_perms = [
        'investigation:create', 'investigation:read', 'investigation:update',
        'collector:execute', 'report:create', 'report:read', 'report:export',
        'user:read'
    ]
    for perm_name in analyst_perms:
        if perm_name in permissions:
            await RBACManager.assign_permission_to_role(db, roles['analyst'], permissions[perm_name])

    # Viewer: read-only permissions
    viewer_perms = ['investigation:read', 'report:read', 'user:read']
    for perm_name in viewer_perms:
        if perm_name in permissions:
            await RBACManager.assign_permission_to_role(db, roles['viewer'], permissions[perm_name])

    # API User: programmatic access
    api_perms = [
        'investigation:create', 'investigation:read',
        'collector:execute', 'report:create', 'report:read'
    ]
    for perm_name in api_perms:
        if perm_name in permissions:
            await RBACManager.assign_permission_to_role(db, roles['api_user'], permissions[perm_name])

    await db.commit()
