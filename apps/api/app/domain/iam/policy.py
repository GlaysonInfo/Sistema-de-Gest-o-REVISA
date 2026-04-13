class PermissionPolicy:
    @staticmethod
    def has_permission(current_user, permission_code: str) -> bool:
        return permission_code in getattr(current_user, "permissions", set()) or getattr(current_user, "is_global_admin", False)
