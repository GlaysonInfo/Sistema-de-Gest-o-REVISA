from fastapi import Depends, HTTPException, status

from app.api.deps.auth import get_current_user
from app.core.permissions import has_permission


def require_permission(permission_code: str):
    def dependency(current_user = Depends(get_current_user)):
        if not has_permission(current_user, permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_code}",
            )
        return current_user
    return dependency
