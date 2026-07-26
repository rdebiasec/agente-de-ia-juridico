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
    # Modelo mas capaz para redaccion/tutela (alto riesgo). Vacio = usa openai_model.
    openai_model_high_risk: str = "gpt-4o"
    # Respaldo operacional; vacío desactiva cambio de modelo en reintento.
    openai_model_fallback: str = ""

    slack_bot_token: str = ""
    # App-level token (xapp-…) for Socket Mode — see docs.slack.dev Socket Mode / Bolt.
    slack_app_token: str = ""
    slack_signing_secret: str = ""
    slack_review_channel: str = "#revision-abogado"
    # CSV de Slack user IDs (U…) autorizados a aprobar/editar/rechazar borradores.
    # Vacío = cualquier miembro del workspace con acceso al canal (solo para local/dev).
    slack_approver_ids: str = ""

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
    # Default más corto para equipos compartidos; Render puede sobreescribir.
    session_idle_minutes: int = 60
    session_max_messages: int = 120
    # Ventana reciente enviada al Runner; el resto se compacta a un resumen extractivo.
    session_recent_messages: int = 16
    # Chat del gerente: clasificar → 0–1 KB → 1 especialista → sintetizar.
    agent_max_turns: int = 10
    # Tope de turnos por paso de plan (Watchdog Timeout / control de costo).
    agent_max_turns_plan_step: int = 6
    # Tope de turnos del agente anidado (as_tool) invocado por el gerente.
    agent_nested_max_turns: int = 3
    # Tope de caracteres del resumen de turnos antiguos en sesión.
    session_summary_max_chars: int = 1200
    agent_run_timeout_seconds: float = 90.0
    agent_plan_step_timeout_seconds: float = 75.0
    agent_max_retries: int = 1
    # Presupuesto por ejecución; 0 desactiva el límite.
    agent_max_total_tokens: int = 30000
    # Un plan executing sin checkpoint reciente se considera huérfano.
    plan_stale_after_seconds: int = 300
    session_cookie_secure: bool = False
    # Solo desarrollo local (.env); bloqueado en Render y con SESSION_COOKIE_SECURE=true.
    dev_auto_login: bool = False
    # Correo con el que /auditoria abre sesión sola cuando DEV_AUTO_LOGIN=true.
    # Úselo con su correo habitual para conservar el progreso guardado en local.
    dev_audit_email: str = ""
    # Telemetría de depuración (middleware /debug/*). Nunca activar en producción.
    app_debug: bool = False
    # Cifrado en reposo (Fernet). Si vacío, se deriva de SESSION_SECRET cuando exista.
    data_at_rest_key: str = ""
    # Lista CSV de correos permitidos en el portal de auditoría.
    # Vacío = cualquier correo válido + SITE_PASSWORD (comportamiento actual).
    audit_allowed_emails: str = ""
    # Observabilidad opcional (Sentry). Vacío = desactivado.
    sentry_dsn: str = ""

    def audit_email_allowlist(self) -> set[str]:
        raw = (self.audit_allowed_emails or "").strip()
        if not raw:
            return set()
        return {e.strip().lower() for e in raw.split(",") if e.strip()}

    def slack_approver_allowlist(self) -> set[str]:
        raw = (self.slack_approver_ids or "").strip()
        if not raw:
            return set()
        return {uid.strip() for uid in raw.split(",") if uid.strip()}

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def agente_dir(self) -> Path:
        return self.project_root / "agente"


@lru_cache
def get_settings() -> Settings:
    return Settings()
