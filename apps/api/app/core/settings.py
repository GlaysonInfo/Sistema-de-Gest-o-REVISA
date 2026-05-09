from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


API_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://revisa:revisa@postgres:5432/revisa"
    test_database_url: str | None = "postgresql+psycopg2://revisa:revisa@postgres:5432/revisa_test"
    jwt_secret_key: str = "change_me"
    jwt_refresh_secret_key: str = "change_me_too"
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=[REPO_ROOT / ".env", API_ROOT / ".env", ".env"],
        extra="ignore",
    )


settings = Settings()
