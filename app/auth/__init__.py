"""
Authentication and authorization module
"""
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_permissions,
    require_roles,
    get_api_key_user,
)
from .oauth2 import oauth2_handler, OAuth2Handler
from .rbac import check_permission, has_role, RBACManager

__all__ = [
    'get_current_user',
    'get_current_active_user',
    'require_permissions',
    'require_roles',
    'get_api_key_user',
    'oauth2_handler',
    'OAuth2Handler',
    'check_permission',
    'has_role',
    'RBACManager',
]
