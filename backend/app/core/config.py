from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://quizai:quizai@localhost:5432/quizai"
    test_database_url: str = "postgresql+psycopg://quizai:quizai@localhost:5432/quizai_test"

    cors_origins: str = "http://localhost:5173"
    storage_dir: Path = Path("./data")

    worker_poll_interval_seconds: float = 1.0
    job_max_attempts: int = 3
    job_visibility_timeout_seconds: int = 300

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
