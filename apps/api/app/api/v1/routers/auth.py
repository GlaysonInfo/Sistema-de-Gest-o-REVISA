from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.core.database import get_db
from app.core.auth import AuthService
from app.domain.iam.repository import IAMRepository

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = AuthService(IAMRepository(db)).login(payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    db.commit()
    return result


@router.get("/me")
def me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "roles": sorted(list(current_user.roles)),
        "permissions": sorted(list(current_user.permissions)),
        "scopes": {k: sorted(list(v)) for k, v in current_user.scope_map.items()},
    }
