# Google Drive Lexiatek — bitácora del Gerente

Shared Drive **Lexiatek** = espejo de lectura de `Expediente.bitacora`.  
Postgres sigue siendo la fuente de verdad. Auth: **service account** (sin OAuth de abogado).

**Entorno actual:** local/dev. No activar en Render con datos reales sin DPA Google + aviso/RNBD.

## Checklist Google (operador)

### A1. Proyecto y API

1. [Google Cloud Console](https://console.cloud.google.com/) → proyecto (ej. `lexiatek-agents`).
2. **APIs y servicios → Biblioteca → Google Drive API → Habilitar**.

### A2. Service account

1. **IAM → Cuentas de servicio → Crear**.
2. Nombre: `lexiatek-drive` → email `lexiatek-drive@PROJECT_ID.iam.gserviceaccount.com`.
3. Rol en el proyecto GCP: ninguno crítico (el acceso es por Shared Drive).
4. **Claves → Agregar clave → JSON** → guardar **fuera del repo**, p. ej.  
   `~/Backups/agente-juridico/secrets/lexiatek-agents-drive-access-key.json`  
   (`chmod 600`). **Nunca** dentro del git working tree (ni carpetas tipo `secure folder/`).
5. Copiar el email de la SA (`client_email` del JSON).
6. Confirmar que **Google Drive API** está habilitada en el **mismo** proyecto GCP de la SA  
   (si el smoke da `accessNotConfigured`, abrir  
   `https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=PROJECT_NUMBER`).

### A3. Carpeta / Shared Drive «Lexiatek»

**Opción recomendada si no aparece «Administrar miembros»:** carpeta en **Mi unidad**.

1. [Google Drive](https://drive.google.com/) → **Mi unidad** → **Nueva carpeta** `Lexiatek`.
2. Clic derecho → **Compartir** → email de la SA → rol **Editor**  
   (el aviso “externo a la organización” es normal para `*.iam.gserviceaccount.com`; aceptar).
3. Copiar el **folder ID** de la URL:  
   `https://drive.google.com/drive/folders/FOLDER_ID`.

**Opción Shared Drive** (si Workspace lo permite):

1. **Unidades compartidas → Nueva → Lexiatek**.
2. **Administrar miembros** (flecha ▼ junto al nombre): SA como **Administrador de contenido**.
3. Opcional: carpeta `casos/` (si no, el sync la crea).
4. Mismo `FOLDER_ID` desde la URL.

### A4. Domain-wide delegation

No suele hacer falta si la SA es miembro del Shared Drive.  
Si hay 403: revisar membresía SA + que el código use `supportsAllDrives=True`.

### A5. Variables `.env` (local)

```bash
GOOGLE_DRIVE_BITACORA_ENABLED=true
GOOGLE_DRIVE_ROOT_FOLDER_ID=...   # Lexiatek o carpetas/casos
GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE=/Users/TU/Backups/agente-juridico/secrets/lexiatek-drive.json
# Alternativa ADC:
# GOOGLE_APPLICATION_CREDENTIALS=/Users/TU/Backups/agente-juridico/secrets/lexiatek-drive.json
```

Instalar deps opcionales:

```bash
pip install '.[drive]'
```

### A6. Smoke

```bash
python scripts/smoke_drive_bitacora.py
```

Debe crear/actualizar `casos/_smoke/bitacora.md` en Lexiatek.

Luego un turno de chat sintético: aparece `casos/<session-sanitizado>/bitacora.md`.

### A7. Cumplimiento

- Solo datos **sintéticos/anonimizados** en local hasta DPA Google.
- Ver [`RUNBOOK_CUMPLIMIENTO_1581.md`](./RUNBOOK_CUMPLIMIENTO_1581.md).
- ARCO: borrar carpeta Drive al erase es **fase 2** (pendiente).

## Estructura esperada

```
Lexiatek/
  casos/
    web-smoke-001/
      bitacora.md
      notepads/                 # F5 — un MD por agent_id
        coordinador_caso.md
        analista_cronologia_hechos.md
        …
    _smoke/
      bitacora.md
```

Notepads por especialista (contrato + sync): [`RUNBOOK_NOTEPADS_DRIVE.md`](./RUNBOOK_NOTEPADS_DRIVE.md).

```bash
python scripts/sync_drive_notepads.py --local-only   # sin API
python scripts/sync_drive_notepads.py                # con SA
```

## Troubleshooting

| Síntoma | Qué revisar |
|--------|-------------|
| `Drive no configurado` | Flag `GOOGLE_DRIVE_BITACORA_ENABLED`, folder id, path JSON |
| `403` | SA miembro del Shared Drive; rol Content manager; API habilitada |
| `404` | `GOOGLE_DRIVE_ROOT_FOLDER_ID` incorrecto |
| `ModuleNotFoundError: googleapiclient` | `pip install '.[drive]'` |
| Chat lento | Sync es best-effort sync; si molesta, desactivar flag |

## Código

- Servicio: `src/services/drive_bitacora.py`
- Enganche: tras append en `src/services/bitacora.py`
- Settings: `google_drive_*` en `src/config.py`
