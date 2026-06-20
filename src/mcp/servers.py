"""MCP filesystem — configuración para entorno con Node/npx."""

from pathlib import Path

from src.config import get_settings


def get_mcp_server_params() -> dict | None:
    """Parámetros MCPServerStdio para leer agente/ vía MCP (requiere npx)."""
    settings = get_settings()
    agente_path = str(settings.agente_dir)
    if not Path(agente_path).exists():
        return None
    return {
        "name": "agente-docs",
        "params": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                agente_path,
            ],
        },
    }
