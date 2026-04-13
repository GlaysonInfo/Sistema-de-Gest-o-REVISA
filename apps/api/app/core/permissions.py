def has_permission(current_user, permission_code: str) -> bool:
    return current_user.is_global_admin or permission_code in current_user.permissions
