from app.core.access_scope import is_revisa_admin


def in_scope(current_user, scope_type: str, scope_ref_id: str | None) -> bool:
    if is_revisa_admin(current_user):
        return True
    if scope_ref_id is None:
        return True
    return scope_ref_id in current_user.scope_map.get(scope_type, set())
