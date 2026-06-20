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

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    redis_url: str = "redis://localhost:6379/0"
    active_phase: int = 0
    require_human_review_whatsapp: bool = True
    # Render inyecta PORT automáticamente; local default 8000
    port: int = 8000  # env: PORT

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def agente_dir(self) -> Path:
        return self.project_root / "agente"


@lru_cache
def get_settings() -> Settings:
    return Settings()
