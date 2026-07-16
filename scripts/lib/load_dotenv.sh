# Carga .env sin expandir $ dentro de valores (crítico para hashes pbkdf2_sha256$…).
# Uso:
#   # shellcheck source=scripts/lib/load_dotenv.sh
#   source "$ROOT/scripts/lib/load_dotenv.sh"
#   load_dotenv "$ROOT/.env"
#
# Requiere Python 3 en PATH (o LOAD_DOTENV_PYTHON).

load_dotenv() {
  local env_file="${1:-.env}"
  local py="${LOAD_DOTENV_PYTHON:-python3}"
  if [[ ! -f "$env_file" ]]; then
    return 0
  fi
  # shellcheck disable=SC1090
  eval "$("$py" - "$env_file" <<'PY'
import shlex
import sys
from pathlib import Path

path = Path(sys.argv[1])
for raw in path.read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, _, value = line.partition("=")
    key = key.strip()
    if not key or not key.replace("_", "").isalnum():
        continue
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    print(f"export {key}={shlex.quote(value)}")
PY
)"
}
