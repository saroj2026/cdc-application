"""Role-Based Access Control (RBAC) for CDC Replication Application."""
from fastapi import HTTPException, Depends
from typing import List, Optional
from ingestion.routers.auth import get_current_user
from ingestion.database.models_db import UserModel, UserRole

# Permission matrix for CDC operations
PERMISSIONS = {
    "create_user": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN],
    "manage_roles": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN],
    "create_connection": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.DATA_ENGINEER],
    "view_credentials": [],  # No one can view credentials
    "test_connection": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.DATA_ENGINEER],
    "create_pipeline": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.DATA_ENGINEER],
    "start_stop_pipeline": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.OPERATOR],
    "pause_pipeline": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.OPERATOR],
    "reset_offsets": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN],  # Sensitive action
    "trigger_full_load": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.DATA_ENGINEER],
    "delete_pipeline": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN],
    "view_metrics": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.DATA_ENGINEER, UserRole.OPERATOR, UserRole.VIEWER],
    "view_audit_logs": [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN],
}


def require_roles(*allowed_roles: UserRole):
    """Dependency to require specific roles for an endpoint."""
    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        user_role = UserRole(current_user.role_name) if hasattr(UserRole, current_user.role_name.upper()) else None
        
        # Super admins can do everything
        if current_user.is_superuser or user_role == UserRole.SUPER_ADMIN:
            return current_user
        
        # Check if user's role is in allowed roles
        if user_role and user_role in allowed_roles:
            return current_user
        
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
        )
    
    return role_checker


def require_permission(permission: str):
    """Dependency to require a specific permission."""
    def permission_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        # Super admins have all permissions
        if current_user.is_superuser:
            return current_user
        
        # Get allowed roles for this permission
        allowed_roles = PERMISSIONS.get(permission, [])
        if not allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' is not available to any role"
            )
        
        # Check if user's role has this permission
        try:
            user_role = UserRole(current_user.role_name)
            if user_role in allowed_roles:
                return current_user
        except (ValueError, AttributeError):
            pass
        
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Permission required: {permission}"
        )
    
    return permission_checker


def require_sensitive_action(current_user: UserModel = Depends(get_current_user)):
    """Dependency for sensitive actions requiring step-up authentication.
    
    For now, this just checks for admin roles. In production, you would:
    - Require password re-entry
    - Or require OTP/email confirmation
    """
    if current_user.is_superuser:
        return current_user
    
    user_role = None
    try:
        user_role = UserRole(current_user.role_name)
    except (ValueError, AttributeError):
        pass
    
    if user_role in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        return current_user
    
    raise HTTPException(
        status_code=403,
        detail="Sensitive action requires administrator privileges"
    )


def get_user_permissions(user: UserModel) -> List[str]:
    """Get list of permissions for a user based on their role."""
    if user.is_superuser:
        return list(PERMISSIONS.keys())
    
    user_permissions = []
    try:
        user_role = UserRole(user.role_name)
        for permission, allowed_roles in PERMISSIONS.items():
            if user_role in allowed_roles:
                user_permissions.append(permission)
    except (ValueError, AttributeError):
        pass
    
    return user_permissions

