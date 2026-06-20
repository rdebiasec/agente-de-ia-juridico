#!/usr/bin/env bash
# Convierte PDF escaneado a Markdown vía Tesseract (spa+eng).
# Uso: ./scripts/ocr-pdf.sh documentos/original/mi-archivo.pdf

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <ruta-del-pdf>" >&2
  exit 1
fi

PDF="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
if [[ ! -f "$PDF" ]]; then
  echo "Archivo no encontrado: $PDF" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASENAME="$(basename "$PDF" .pdf)"
OUT="$ROOT/documentos/texto/${BASENAME}.md"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

export PATH="/opt/homebrew/bin:${PATH:-}"

if ! command -v pdftoppm >/dev/null || ! command -v tesseract >/dev/null; then
  echo "Instala dependencias: brew install tesseract tesseract-lang poppler" >&2
  exit 1
fi

pdftoppm -png "$PDF" "$TMPDIR/page"

{
  echo "# ${BASENAME}"
  echo ""
  echo "Fuente: documentos/original/$(basename "$PDF")"
  echo "Fecha OCR: $(date +%Y-%m-%d)"
  echo "Idioma OCR: spa+eng"
  echo ""
  echo "## Contenido"
  echo ""

  for img in "$TMPDIR"/page-*.png; do
    page="$(basename "$img" .png)"
    page_num="${page#page-}"
    echo "### Página ${page_num}"
    echo ""
    tesseract "$img" stdout -l spa+eng 2>/dev/null
    echo ""
  done
} > "$OUT"

echo "Generado: $OUT"
