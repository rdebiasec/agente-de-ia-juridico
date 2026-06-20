#!/usr/bin/env bash
# Crea el repo agente-de-ia-juridico en GitHub y hace push.
# Requisito: gh auth login (una sola vez)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REPO_NAME="agente-de-ia-juridico"

if ! gh auth status >/dev/null 2>&1; then
  echo "Primero autentícate en GitHub:"
  echo "  gh auth login"
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Remote origin ya existe:"
  git remote -v
else
  gh repo create "$REPO_NAME" \
    --private \
    --source=. \
    --remote=origin \
    --description="Asistente jurídico multi-agente Fase 0 — Slack + WhatsApp" \
    --push
  echo "Repo creado y push hecho: https://github.com/$(gh api user -q .login)/$REPO_NAME"
  exit 0
fi

git push -u origin main
echo "Push completado."
