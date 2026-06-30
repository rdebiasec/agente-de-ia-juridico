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

    # Twilio SMS — alertas transaccionales de plazos (complemento a Slack).
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_messaging_service_sid: str = ""
    twilio_from_number: str = ""
    twilio_alert_to: str = ""
    twilio_status_callback: str = ""

    # Persistencia (Fase B). Vacío => repositorio en memoria (tests / local sin Docker).
    # Con valor (p. ej. postgresql+psycopg://...) => backend Postgres/pgvector.
    database_url: str = ""
    embedding_model: str = "text-embedding-3-small"

    redis_url: str = "redis://localhost:6379/0"
    require_human_review_web: bool = True
    # Render inyecta PORT automáticamente; local default 8000
    port: int = 8000  # env: PORT

    site_username: str = "despacho"
    # Sin valores por defecto débiles: configurar en .env local o secretos de Render.
    site_password: str = ""
    session_secret: str = ""
    session_idle_minutes: int = 360
    session_max_messages: int = 120
    agent_max_turns: int = 25
    session_cookie_secure: bool = False
    # Solo desarrollo local (.env); bloqueado en Render y con SESSION_COOKIE_SECURE=true.
    dev_auto_login: bool = False
    # Telemetría de depuración (middleware /debug/*). Nunca activar en producción.
    app_debug: bool = False

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def agente_dir(self) -> Path:
        return self.project_root / "agente"


@lru_cache
def get_settings() -> Settings:
    return Settings()
