from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.iam.models import Permission, RefreshToken, Role, RolePermission, User, UserRole, UserScopeAssignment


class IAMRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalars().first()

    def get_user_by_id(self, user_id: str) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalars().first()

    def get_role_codes(self, user_id: str) -> list[str]:
        stmt = (
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_permission_codes(self, user_id: str) -> list[str]:
        stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return list(set(self.db.execute(stmt).scalars().all()))

    def get_scopes(self, user_id: str) -> list[UserScopeAssignment]:
        stmt = select(UserScopeAssignment).where(UserScopeAssignment.user_id == user_id)
        return list(self.db.execute(stmt).scalars().all())

    def save_refresh_token(self, entity: RefreshToken) -> RefreshToken:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity
