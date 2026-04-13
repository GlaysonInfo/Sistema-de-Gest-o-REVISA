from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://revisa:revisa@localhost:5432/revisa"
    test_database_url: str | None = "postgresql+psycopg://revisa:revisa@localhost:5432/revisa_test"
    jwt_secret_key: str = "change_me"
    jwt_refresh_secret_key: str = "change_me_too"
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=[REPO_ROOT / ".env", ".env"],
        extra="ignore",
    )


settings = Settings()
