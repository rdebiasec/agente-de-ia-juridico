"""Almacén versionado de configuración operativa (prompts, guardrails, skills).

Postgres es la fuente autoritativa en runtime. Los archivos en disco son
baseline/seed y exportación legible para desarrollo.
"""

from src.config_store.paths import KIND_GUARDRAIL, KIND_PROMPT, KIND_SKILL, path_for
from src.config_store.service import (
    ConfigConflictError,
    ConfigNotFoundError,
    ConfigValidationError,
    get_active_content,
    list_catalog_items,
    list_versions,
    load_guardrail_policies,
    load_prompt_text,
    restore_version,
    save_version,
    seed_from_filesystem,
    validate_config_store,
)

__all__ = [
    "KIND_GUARDRAIL",
    "KIND_PROMPT",
    "KIND_SKILL",
    "ConfigConflictError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "get_active_content",
    "list_catalog_items",
    "list_versions",
    "load_guardrail_policies",
    "load_prompt_text",
    "path_for",
    "restore_version",
    "save_version",
    "seed_from_filesystem",
    "validate_config_store",
]
