import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.domain.iam.models import Permission, Role, RolePermission


ROLES = [
    ("ADM_GERAL_REVISA", "Administrador Geral REVISA"),
    ("ADM_REVISA", "Administrador REVISA"),
    ("AUXILIAR_ADM_REVISA", "Auxiliar Administrativo REVISA"),
    ("GESTOR_RH", "Gestor RH REVISA"),
    ("GESTOR_FINANCEIRO", "Gestor Financeiro REVISA"),
    ("VEREADOR", "Vereador"),
    ("CHEFE_GABINETE", "Chefe de Gabinete"),
    ("SUPERVISOR_EQUIPE_POLITICA", "Supervisor de Equipe Politica"),
    ("ADM_POLO", "Administrador do Polo"),
    ("COORDENADOR_POLO", "Coordenador do Polo"),
    ("COLABORADOR_POLO", "Colaborador do Polo"),
    ("COLABORADOR_GABINETE", "Colaborador de Gabinete"),
    ("COLABORADOR_REVISA", "Colaborador REVISA"),
    ("BENEFICIARIO", "Beneficiario"),
    ("EMPRESA_PARCEIRA", "Empresa Parceira"),
    ("VOLUNTARIO_AUTOINSCRITO", "Voluntario Autoinscrito"),
]

PERMISSIONS = [
    "auth.login",
    "user.read",
    "user.create",
    "user.update",
    "user.manage_roles",
    "user.manage_scopes",
    "organization.read",
    "organization.create",
    "organization.update",
    "vereador.read",
    "vereador.create",
    "vereador.update",
    "team.read",
    "team.create",
    "team.update",
    "person.read",
    "person.create",
    "person.update",
    "person.link",
    "consent.read",
    "consent.create",
    "consent.revoke",
    "capture.read",
    "capture.create",
    "capture.classify",
    "capture.forward",
    "capture.convert",
    "polo.read",
    "polo.create",
    "polo.update",
    "polo.manage_beneficiary",
    "modality.read",
    "modality.create",
    "modality.update",
    "attendance.read",
    "attendance.create",
    "occurrence.read",
    "occurrence.create",
    "daily_log.read",
    "daily_log.create",
    "purchase_request.read",
    "purchase_request.create",
    "administration.read",
    "administration.manage_finance",
    "administration.manage_contract",
    "administration.manage_purchase",
    "administration.manage_staff",
    "cabinet.read",
    "cabinet.action.read",
    "cabinet.action.create",
    "task.read",
    "task.create",
    "task.update",
    "task.complete",
    "demand.read",
    "demand.create",
    "demand.update",
    "demand.assign",
    "event.read",
    "event.create",
    "event.update",
    "dashboard.admin.read",
    "dashboard.vereador.read",
    "dashboard.polo.read",
    "dashboard.cabinet.read",
    "geo.read",
    "geo.manage",
    "report.read",
    "report.export",
    "audit.read",
    "privacy.read",
    "privacy.process",
]

ROLE_PERMISSIONS = {
    "ADM_GERAL_REVISA": PERMISSIONS,
    "ADM_REVISA": PERMISSIONS,
    "AUXILIAR_ADM_REVISA": [
        "organization.read",
        "vereador.read",
        "person.read",
        "polo.read",
        "modality.read",
        "attendance.read",
        "occurrence.read",
        "daily_log.read",
        "purchase_request.read",
        "purchase_request.create",
        "administration.read",
        "administration.manage_purchase",
        "task.read",
        "demand.read",
        "event.read",
        "dashboard.admin.read",
        "dashboard.polo.read",
        "report.read",
        "report.export",
    ],
    "GESTOR_RH": [
        "user.read",
        "organization.read",
        "vereador.read",
        "person.read",
        "person.create",
        "person.update",
        "person.link",
        "consent.read",
        "polo.read",
        "polo.update",
        "polo.manage_beneficiary",
        "modality.read",
        "attendance.read",
        "occurrence.read",
        "daily_log.read",
        "purchase_request.read",
        "administration.read",
        "administration.manage_contract",
        "administration.manage_staff",
        "task.read",
        "task.create",
        "task.update",
        "task.complete",
        "demand.read",
        "demand.create",
        "demand.update",
        "dashboard.admin.read",
        "dashboard.polo.read",
        "report.read",
        "report.export",
        "audit.read",
    ],
    "GESTOR_FINANCEIRO": [
        "user.read",
        "organization.read",
        "vereador.read",
        "person.read",
        "polo.read",
        "modality.read",
        "attendance.read",
        "occurrence.read",
        "purchase_request.read",
        "purchase_request.create",
        "administration.read",
        "administration.manage_finance",
        "administration.manage_contract",
        "administration.manage_purchase",
        "administration.manage_staff",
        "task.read",
        "demand.read",
        "dashboard.admin.read",
        "dashboard.polo.read",
        "report.read",
        "report.export",
        "audit.read",
    ],
    "VEREADOR": [
        "cabinet.read",
        "capture.read",
        "demand.read",
        "task.read",
        "event.read",
        "dashboard.vereador.read",
        "report.read",
        "geo.read",
    ],
    "CHEFE_GABINETE": [
        "team.read",
        "person.read",
        "person.link",
        "consent.read",
        "capture.read",
        "capture.create",
        "capture.classify",
        "capture.forward",
        "cabinet.read",
        "cabinet.action.read",
        "cabinet.action.create",
        "task.read",
        "task.create",
        "task.update",
        "task.complete",
        "demand.read",
        "demand.create",
        "demand.update",
        "demand.assign",
        "event.read",
        "event.create",
        "event.update",
        "dashboard.cabinet.read",
        "report.read",
        "geo.read",
    ],
    "SUPERVISOR_EQUIPE_POLITICA": [
        "team.read",
        "person.read",
        "capture.read",
        "capture.create",
        "capture.classify",
        "cabinet.read",
        "cabinet.action.read",
        "cabinet.action.create",
        "task.read",
        "task.create",
        "task.update",
        "task.complete",
        "demand.read",
        "demand.create",
        "demand.update",
        "event.read",
        "event.create",
        "dashboard.cabinet.read",
        "report.read",
    ],
    "ADM_POLO": [
        "polo.read",
        "polo.update",
        "polo.manage_beneficiary",
        "modality.read",
        "modality.create",
        "modality.update",
        "attendance.read",
        "attendance.create",
        "occurrence.read",
        "occurrence.create",
        "daily_log.read",
        "daily_log.create",
        "purchase_request.read",
        "purchase_request.create",
        "administration.read",
        "administration.manage_finance",
        "administration.manage_contract",
        "administration.manage_purchase",
        "administration.manage_staff",
        "task.read",
        "task.create",
        "task.update",
        "task.complete",
        "demand.read",
        "demand.create",
        "demand.update",
        "event.read",
        "event.create",
        "event.update",
        "dashboard.polo.read",
        "report.read",
        "geo.read",
    ],
    "COORDENADOR_POLO": [
        "polo.read",
        "polo.manage_beneficiary",
        "modality.read",
        "modality.create",
        "modality.update",
        "attendance.read",
        "attendance.create",
        "occurrence.read",
        "occurrence.create",
        "daily_log.read",
        "daily_log.create",
        "purchase_request.read",
        "purchase_request.create",
        "administration.read",
        "administration.manage_purchase",
        "task.read",
        "task.create",
        "task.update",
        "task.complete",
        "demand.read",
        "demand.create",
        "demand.update",
        "event.read",
        "event.create",
        "dashboard.polo.read",
        "report.read",
    ],
    "COLABORADOR_POLO": [
        "polo.read",
        "attendance.create",
        "attendance.read",
        "occurrence.create",
        "occurrence.read",
        "daily_log.create",
        "daily_log.read",
        "task.read",
        "task.update",
        "task.complete",
        "demand.read",
        "demand.create",
        "event.read",
    ],
    "COLABORADOR_GABINETE": [
        "person.read",
        "capture.create",
        "capture.read",
        "demand.create",
        "demand.read",
        "task.read",
        "task.update",
        "task.complete",
        "event.read",
    ],
    "COLABORADOR_REVISA": [
        "person.read",
        "person.create",
        "person.update",
        "consent.create",
        "capture.read",
        "capture.create",
        "demand.read",
        "demand.create",
        "event.read",
        "report.read",
    ],
    "BENEFICIARIO": [],
    "EMPRESA_PARCEIRA": ["event.read"],
    "VOLUNTARIO_AUTOINSCRITO": [],
}


def ensure_role(db, code: str, name: str) -> Role:
    role = db.execute(select(Role).where(Role.code == code)).scalars().first()
    if role:
        return role
    role = Role(id=uuid4(), code=code, name=name)
    db.add(role)
    db.flush()
    return role


def ensure_permission(db, code: str) -> Permission:
    permission = db.execute(select(Permission).where(Permission.code == code)).scalars().first()
    if permission:
        return permission
    permission = Permission(id=uuid4(), code=code, name=code)
    db.add(permission)
    db.flush()
    return permission


def ensure_role_permission(db, role: Role, permission: Permission) -> None:
    exists = db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
    ).scalars().first()
    if exists:
        return
    db.add(RolePermission(id=uuid4(), role_id=role.id, permission_id=permission.id))


def main() -> None:
    db = SessionLocal()
    try:
        roles = {code: ensure_role(db, code, name) for code, name in ROLES}
        permissions = {code: ensure_permission(db, code) for code in PERMISSIONS}

        for role_code, permission_codes in ROLE_PERMISSIONS.items():
            role = roles[role_code]
            for permission_code in permission_codes:
                ensure_role_permission(db, role, permissions[permission_code])

        db.commit()
        print("seeds iniciais aplicados")
    finally:
        db.close()


if __name__ == "__main__":
    main()
