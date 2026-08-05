"""Almacén versionado de configuración operativa (prompts, guardrails, skills).

Postgres es la fuente autoritativa en runtime. Los archivos en disco son
baseline/seed y exportación legible para desarrollo.
"""

from src.config_store.paths import (
    KIND_AGENT_GUARDRAIL,
    KIND_GUARDRAIL,
    KIND_PROMPT,
    KIND_SKILL,
    path_for,
)
from src.config_store.service import (
    ConfigConflictError,
    ConfigNotFoundError,
    ConfigValidationError,
    ensure_agent_guardrail_seeds,
    get_active_content,
    list_catalog_items,
    list_orphan_config_keys,
    list_versions,
    load_guardrail_policies,
    load_prompt_text,
    parse_header,
    restore_version,
    retire_config_key,
    save_version,
    seed_from_filesystem,
    validate_config_store,
)
from src.config_store.sync import (
    ConfigDiff,
    diff_item,
    export_to_file,
    import_to_db,
    iter_diffs,
    refresh_header,
)

__all__ = [
    "KIND_AGENT_GUARDRAIL",
    "KIND_GUARDRAIL",
    "KIND_PROMPT",
    "KIND_SKILL",
    "ConfigConflictError",
    "ConfigDiff",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "diff_item",
    "ensure_agent_guardrail_seeds",
    "export_to_file",
    "get_active_content",
    "import_to_db",
    "iter_diffs",
    "list_catalog_items",
    "list_orphan_config_keys",
    "list_versions",
    "load_guardrail_policies",
    "load_prompt_text",
    "parse_header",
    "path_for",
    "refresh_header",
    "restore_version",
    "retire_config_key",
    "save_version",
    "seed_from_filesystem",
    "validate_config_store",
]
