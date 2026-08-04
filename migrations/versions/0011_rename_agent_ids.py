"""Rename agent IDs in config_active / config_versions (prompts + agent_guardrails)

Revision ID: 0011
Revises: 0010
Create Date: 2026-08-03

Maps legacy agent IDs to canonical names after the product rename.
Also rewrites config_active.path and body content that embeds old IDs.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

# old → new (longest-first for content replace)
AGENT_ID_MAP: list[tuple[str, str]] = [
    ("analista_tipicidad_y_responsabilidad_penal", "analista_responsabilidad_tipicidad"),
    ("preparador_estrategico_audiencias_penales", "analista_audiencias"),
    ("gestor_evidencia_y_soporte_probatorio", "analista_evidencia"),
    ("redactor_documentos_juridicos_penales", "redactor_documentos_juridicos"),
    ("gestor_seguimiento_procesal_penal", "analista_seguimiento_procesal"),
    ("analista_cronologia_hechos_penales", "analista_cronologia_hechos"),
    ("analista_ruta_procesal_ley906", "analista_ruta_procesal"),
    ("coordinador_expediente_penal", "coordinador_caso"),
]

GUARDRAIL_CLASSES = ("input", "output", "tools")


def _key_renames() -> list[tuple[str, str, str]]:
    """Return list of (kind, old_key, new_key)."""
    rows: list[tuple[str, str, str]] = []
    for old, new in AGENT_ID_MAP:
        rows.append(("prompt", old, new))
        for clase in GUARDRAIL_CLASSES:
            rows.append(("agent_guardrail", f"{old}__{clase}", f"{new}__{clase}"))
    return rows


def _agent_frag(key: str) -> str:
    return key.split("__", 1)[0]


def upgrade() -> None:
    conn = op.get_bind()

    # Tutela specialist removed from product — drop leftover config rows.
    for kind, key in (
        ("prompt", "evaluador_derechos_fundamentales_tutela"),
        ("agent_guardrail", "evaluador_derechos_fundamentales_tutela__output"),
        ("agent_guardrail", "evaluador_derechos_fundamentales_tutela__input"),
        ("agent_guardrail", "evaluador_derechos_fundamentales_tutela__tools"),
    ):
        conn.execute(
            sa.text("DELETE FROM config_active WHERE kind = :k AND key = :key"),
            {"k": kind, "key": key},
        )
        conn.execute(
            sa.text("DELETE FROM config_versions WHERE kind = :k AND key = :key"),
            {"k": kind, "key": key},
        )

    for kind, old_key, new_key in _key_renames():
        exists_new = conn.execute(
            sa.text(
                "SELECT 1 FROM config_active WHERE kind = :k AND key = :key LIMIT 1"
            ),
            {"k": kind, "key": new_key},
        ).fetchone()
        exists_old = conn.execute(
            sa.text(
                "SELECT 1 FROM config_active WHERE kind = :k AND key = :key LIMIT 1"
            ),
            {"k": kind, "key": old_key},
        ).fetchone()
        if exists_old and not exists_new:
            conn.execute(
                sa.text(
                    "UPDATE config_active SET key = :new_key, "
                    "path = REPLACE(path, :old_frag, :new_frag) "
                    "WHERE kind = :k AND key = :old_key"
                ),
                {
                    "new_key": new_key,
                    "old_frag": _agent_frag(old_key),
                    "new_frag": _agent_frag(new_key),
                    "k": kind,
                    "old_key": old_key,
                },
            )
        elif exists_old and exists_new:
            conn.execute(
                sa.text("DELETE FROM config_active WHERE kind = :k AND key = :old_key"),
                {"k": kind, "old_key": old_key},
            )

        old_versions = conn.execute(
            sa.text(
                "SELECT id, version FROM config_versions "
                "WHERE kind = :k AND key = :old_key"
            ),
            {"k": kind, "old_key": old_key},
        ).fetchall()
        for ver_id, version in old_versions:
            clash = conn.execute(
                sa.text(
                    "SELECT 1 FROM config_versions "
                    "WHERE kind = :k AND key = :new_key AND version = :v LIMIT 1"
                ),
                {"k": kind, "new_key": new_key, "v": version},
            ).fetchone()
            if clash:
                conn.execute(
                    sa.text("DELETE FROM config_versions WHERE id = :id"),
                    {"id": ver_id},
                )
            else:
                conn.execute(
                    sa.text(
                        "UPDATE config_versions SET key = :new_key WHERE id = :id"
                    ),
                    {"new_key": new_key, "id": ver_id},
                )

    # Rewrite bodies that still mention old agent IDs
    content_rows = conn.execute(
        sa.text(
            "SELECT id, content FROM config_versions "
            "WHERE kind IN ('skill', 'prompt', 'agent_guardrail')"
        )
    ).fetchall()
    for ver_id, content in content_rows:
        if not content:
            continue
        new_content = content
        for old, new in AGENT_ID_MAP:
            new_content = new_content.replace(old, new)
        new_content = new_content.replace("Gerente del Caso Penal", "Coordinador del Caso")
        new_content = new_content.replace("Gerente del Caso", "Coordinador del Caso")
        if new_content != content:
            conn.execute(
                sa.text("UPDATE config_versions SET content = :c WHERE id = :id"),
                {"c": new_content, "id": ver_id},
            )


def downgrade() -> None:
    """Best-effort reverse rename (new → old)."""
    conn = op.get_bind()
    reverse = [(new, old) for old, new in AGENT_ID_MAP]
    rows: list[tuple[str, str, str]] = []
    for new, old in reverse:
        rows.append(("prompt", new, old))
        for clase in GUARDRAIL_CLASSES:
            rows.append(("agent_guardrail", f"{new}__{clase}", f"{old}__{clase}"))

    for kind, old_key, new_key in rows:
        exists_new = conn.execute(
            sa.text(
                "SELECT 1 FROM config_active WHERE kind = :k AND key = :key LIMIT 1"
            ),
            {"k": kind, "key": new_key},
        ).fetchone()
        exists_old = conn.execute(
            sa.text(
                "SELECT 1 FROM config_active WHERE kind = :k AND key = :key LIMIT 1"
            ),
            {"k": kind, "key": old_key},
        ).fetchone()
        if exists_old and not exists_new:
            conn.execute(
                sa.text(
                    "UPDATE config_active SET key = :new_key, "
                    "path = REPLACE(path, :old_frag, :new_frag) "
                    "WHERE kind = :k AND key = :old_key"
                ),
                {
                    "new_key": new_key,
                    "old_frag": _agent_frag(old_key),
                    "new_frag": _agent_frag(new_key),
                    "k": kind,
                    "old_key": old_key,
                },
            )
        elif exists_old and exists_new:
            conn.execute(
                sa.text("DELETE FROM config_active WHERE kind = :k AND key = :old_key"),
                {"k": kind, "old_key": old_key},
            )

        old_versions = conn.execute(
            sa.text(
                "SELECT id, version FROM config_versions "
                "WHERE kind = :k AND key = :old_key"
            ),
            {"k": kind, "old_key": old_key},
        ).fetchall()
        for ver_id, version in old_versions:
            clash = conn.execute(
                sa.text(
                    "SELECT 1 FROM config_versions "
                    "WHERE kind = :k AND key = :new_key AND version = :v LIMIT 1"
                ),
                {"k": kind, "new_key": new_key, "v": version},
            ).fetchone()
            if clash:
                conn.execute(
                    sa.text("DELETE FROM config_versions WHERE id = :id"),
                    {"id": ver_id},
                )
            else:
                conn.execute(
                    sa.text(
                        "UPDATE config_versions SET key = :new_key WHERE id = :id"
                    ),
                    {"new_key": new_key, "id": ver_id},
                )
