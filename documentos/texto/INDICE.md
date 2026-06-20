# Índice documental

Base de conocimiento en texto (OCR) para usar con `@` en Cursor.

| Archivo | Fuente PDF | Descripción |
|---------|------------|-------------|
| [GUIA_PROYECTO_AGENTE_JURIDICO.md](GUIA_PROYECTO_AGENTE_JURIDICO.md) | `documentos/original/GUIA_PROYECTO_AGENTE_JURIDICO.pdf` | Guía del proyecto del agente jurídico de IA |
| [scan-2022-10-18.md](scan-2022-10-18.md) | `documentos/original/scan-2022-10-18.pdf` | Acción de protección por violencia intrafamiliar — Comisaría Kennedy V (Colombia) |

## Cómo agregar nuevos documentos

1. Coloca el PDF escaneado en `documentos/original/`
2. Ejecuta: `./scripts/ocr-pdf.sh documentos/original/tu-archivo.pdf`
3. Actualiza esta tabla con el nuevo `.md`
4. En el chat de Cursor, usa `@INDICE.md` o `@documentos/texto/tu-archivo.md`
