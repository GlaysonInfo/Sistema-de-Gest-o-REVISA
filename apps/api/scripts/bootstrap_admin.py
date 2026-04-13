import sys
import uuid
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domain.iam.models import Role, User, UserRole


def main():
    db = SessionLocal()
    try:
        user = db.execute(select(User).where(User.username == "admin")).scalars().first()
        if user:
            print("admin já existe")
        else:
            user = User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@revisa.local",
                password_hash=hash_password("Admin@123"),
                status="ACTIVE",
            )
            db.add(user)
            db.flush()
            print("admin criado")

        admin_role = db.execute(select(Role).where(Role.code == "ADM_GERAL_REVISA")).scalars().first()
        if admin_role:
            link = db.execute(
                select(UserRole).where(
                    UserRole.user_id == user.id,
                    UserRole.role_id == admin_role.id,
                )
            ).scalars().first()
            if not link:
                db.add(UserRole(id=uuid.uuid4(), user_id=user.id, role_id=admin_role.id, is_primary=True))

        db.commit()
        print("bootstrap administrativo concluído")
    finally:
        db.close()


if __name__ == "__main__":
    main()
