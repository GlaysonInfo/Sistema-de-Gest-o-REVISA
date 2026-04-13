import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.core.security import hash_password
from app.core.settings import settings
from app.domain.iam.models import Role, User, UserRole
from app.main import app

API_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ("administration", "relationship", "analytics", "governance", "workflow", "events", "polo", "territory", "core", "iam")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", settings.test_database_url or settings.database_url)

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _alembic_config() -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    return config


def _reset_database() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Integration tests require PostgreSQL because migrations use PostgreSQL schemas.")
    with engine.begin() as connection:
        for schema in SCHEMAS:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))


def _truncate_business_tables() -> None:
    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                select schemaname, tablename
                from pg_tables
                where schemaname = any(:schemas)
                """
            ),
            {"schemas": list(SCHEMAS)},
        ).all()
        if not rows:
            return
        table_names = ", ".join(f'"{schema}"."{table}"' for schema, table in rows)
        connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session", autouse=True)
def migrated_test_db():
    previous_url = os.environ.get("ALEMBIC_DATABASE_URL")
    os.environ["ALEMBIC_DATABASE_URL"] = TEST_DATABASE_URL
    _reset_database()
    command.upgrade(_alembic_config(), "head")
    yield
    _reset_database()
    if previous_url is None:
        os.environ.pop("ALEMBIC_DATABASE_URL", None)
    else:
        os.environ["ALEMBIC_DATABASE_URL"] = previous_url


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        _truncate_business_tables()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session):
    user = User(
        username="admin",
        email="admin@revisa.local",
        password_hash=hash_password("Admin@123"),
        status="ACTIVE",
    )
    role = Role(code="ADM_GERAL_REVISA", name="Administrador Geral REVISA")
    db_session.add_all([user, role])
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id, is_primary=True))
    db_session.commit()
    return user


@pytest.fixture()
def auth_headers(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": admin_user.username, "password": "Admin@123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
