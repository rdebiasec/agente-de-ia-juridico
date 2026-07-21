"""Cifrado en reposo y flags de sensibilidad."""

from src.compliance.crypto_at_rest import decrypt_text, encrypt_text, encryption_enabled
from src.services.expediente_sync import sync_expediente_from_chat
from src.storage import get_repository, reset_repository
from src.storage.models import Draft


def test_encrypt_roundtrip_with_session_secret(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    monkeypatch.setenv("DATA_AT_REST_KEY", "")
    get_settings.cache_clear()
    assert encryption_enabled()
    cipher = encrypt_text("memorial confidencial")
    assert cipher.startswith("enc:v1:")
    assert decrypt_text(cipher) == "memorial confidencial"
    get_settings.cache_clear()


def test_draft_stored_encrypted_in_memory(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    monkeypatch.setenv("DATABASE_URL", "")
    get_settings.cache_clear()
    reset_repository()
    repo = get_repository()
    draft = Draft(session_id="web:x", contenido="texto sensible víctima", tipo="memorial", titulo="t")
    repo.add_draft(draft)
    raw = repo._drafts[draft.id]  # type: ignore[attr-defined]
    assert str(raw.contenido).startswith("enc:v1:")
    loaded = repo.get_draft(draft.id)
    assert loaded and loaded.contenido == "texto sensible víctima"
    get_settings.cache_clear()


def test_sync_detects_menor_and_sensible():
    reset_repository()
    out = sync_expediente_from_chat(
        "web:flags-test",
        "La víctima es menor de edad y hay violencia intrafamiliar.",
        [],
    )
    assert "involucra_menor=true" in out["cambios"]
    assert "datos_sensibles=true" in out["cambios"]
    exp = get_repository().get_expediente("web:flags-test")
    assert exp and exp.involucra_menor and exp.datos_sensibles
