from fastapi import HTTPException, status

from app.core.scope import in_scope


def ensure_scope(current_user, scope_type: str, scope_ref_id: str | None):
    if not in_scope(current_user, scope_type, scope_ref_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Out of scope: {scope_type}",
        )
