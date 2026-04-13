REVISA_ADMIN_ROLES = {"ADM_GERAL_REVISA", "ADM_REVISA"}
REVISA_POLO_OPERATION_ROLES = {
    "AUXILIAR_ADM_REVISA",
    "GESTOR_RH",
    "GESTOR_FINANCEIRO",
    "COLABORADOR_REVISA",
}
REVISA_FINANCE_ROLES = {"GESTOR_RH", "GESTOR_FINANCEIRO"}


def user_roles(current_user) -> set[str]:
    return set(getattr(current_user, "roles", set()) or set())


def is_revisa_admin(current_user) -> bool:
    return bool(user_roles(current_user) & REVISA_ADMIN_ROLES) or bool(getattr(current_user, "is_global_admin", False))


def can_access_all_polos(current_user) -> bool:
    return is_revisa_admin(current_user) or bool(user_roles(current_user) & REVISA_POLO_OPERATION_ROLES)


def can_access_all_finance(current_user) -> bool:
    return is_revisa_admin(current_user) or bool(user_roles(current_user) & REVISA_FINANCE_ROLES)


def can_access_all_cabinets(current_user) -> bool:
    return is_revisa_admin(current_user)


def scoped_ids(current_user, scope_type: str) -> set[str]:
    return set(getattr(current_user, "scope_map", {}).get(scope_type, set()) or set())
