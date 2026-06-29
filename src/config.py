from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.is_file() else None,
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_review_channel: str = "#revision-abogado"

    # Persistencia (Fase B). Vacío => repositorio en memoria (tests / local sin Docker).
    # Con valor (p. ej. postgresql+psycopg://...) => backend Postgres/pgvector.
    database_url: str = ""
    embedding_model: str = "text-embedding-3-small"

    redis_url: str = "redis://localhost:6379/0"
    require_human_review_web: bool = True
    # Render inyecta PORT automáticamente; local default 8000
    port: int = 8000  # env: PORT

    site_username: str = "despacho"
    # Mantener auth web activo por defecto para paridad local/producción.
    site_password: str = "Kx9mP2vL8nQw4RsT"
    session_secret: str = "f7a9c2e1b4d6083a5f2e9c1b7d4a608"
    session_idle_minutes: int = 360
    session_max_messages: int = 120
    agent_max_turns: int = 25
    session_cookie_secure: bool = False
    # Solo desarrollo local (.env); bloqueado en Render y con SESSION_COOKIE_SECURE=true.
    dev_auto_login: bool = False

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def agente_dir(self) -> Path:
        return self.project_root / "agente"


@lru_cache
def get_settings() -> Settings:
    return Settings()
