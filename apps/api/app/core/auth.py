from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from app.core.security import create_access_token, create_refresh_token, decode_access_token, verify_password
from app.domain.iam.models import RefreshToken
from app.domain.iam.repository import IAMRepository


@dataclass
class CurrentUser:
    id: str
    username: str
    email: str
    roles: set[str]
    permissions: set[str]
    scope_map: dict[str, set[str]]
    is_global_admin: bool

    @property
    def allowed_polo_ids(self) -> set[str]:
        return self.scope_map.get("POLO", set())

    @property
    def allowed_gabinete_ids(self) -> set[str]:
        return self.scope_map.get("GABINETE", set())

    @property
    def allowed_vereador_ids(self) -> set[str]:
        return self.scope_map.get("VEREADOR", set())


class AuthService:
    def __init__(self, repo: IAMRepository):
        self.repo = repo

    def login(self, username: str, password: str):
        user = self.repo.get_user_by_username(username)
        if not user or user.status != "ACTIVE":
            return None
        if not verify_password(password, user.password_hash):
            return None

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        refresh_hash = sha256(refresh_token.encode()).hexdigest()
        self.repo.save_refresh_token(
            RefreshToken(
                user_id=user.id,
                token_hash=refresh_hash,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 1800,
        }

    def build_current_user(self, access_token: str) -> CurrentUser:
        payload = decode_access_token(access_token)
        user_id = payload["sub"]
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        roles = set(self.repo.get_role_codes(user_id))
        permissions = set(self.repo.get_permission_codes(user_id))
        scopes = self.repo.get_scopes(user_id)
        scope_map: dict[str, set[str]] = {}
        for scope in scopes:
            scope_map.setdefault(scope.scope_type, set()).add(str(scope.scope_ref_id))

        return CurrentUser(
            id=str(user.id),
            username=user.username,
            email=user.email,
            roles=roles,
            permissions=permissions,
            scope_map=scope_map,
            is_global_admin=bool(roles & {"ADM_GERAL_REVISA", "ADM_REVISA"}),
        )
