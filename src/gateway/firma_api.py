"""Endpoints de la firma: bandeja HITL de borradores, documentos y términos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from datetime import date

from src.auth.deps import require_web_session
from src.hitl import drafts as hitl
from src.hitl.drafts import TransicionInvalida
from src.services import rag
from src.services.documentos import docx_desde_borrador, extraer_texto, generar_pdf_desde_borrador
from src.services.plazos import crear_termino
from src.storage import get_repository
from src.storage.models import ESTADO_PROPUESTO

router = APIRouter(dependencies=[Depends(require_web_session)])

_DOCX_MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class AprobarRequest(BaseModel):
    revisor: str = "abogado"
    comentario: str | None = None


class RechazarRequest(BaseModel):
    revisor: str = "abogado"
    comentario: str


class EditarRequest(BaseModel):
    revisor: str = "abogado"
    contenido: str
    comentario: str | None = None


class ExpedienteFlagsRequest(BaseModel):
    session_id: str
    involucra_menor: bool | None = None
    datos_sensibles: bool | None = None


@router.patch("/expediente/flags")
async def actualizar_flags_expediente(req: ExpedienteFlagsRequest):
    """Marca menor / datos sensibles para reforzar minimización (Ley 1581)."""
    from src.gateway.expediente import expediente_store

    if not req.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id requerido.")
    campos = {}
    if req.involucra_menor is not None:
        campos["involucra_menor"] = req.involucra_menor
    if req.datos_sensibles is not None:
        campos["datos_sensibles"] = req.datos_sensibles
    if not campos:
        raise HTTPException(status_code=400, detail="Sin cambios.")
    exp = expediente_store.update(req.session_id.strip(), **campos)
    return {"ok": True, "expediente": exp.to_dict()}


@router.get("/drafts")
async def listar_borradores(estado: str | None = None, session_id: str | None = None):
    repo = get_repository()
    items = repo.list_drafts(estado=estado, session_id=session_id)
    return {"drafts": [d.to_dict() for d in items]}


@router.get("/drafts/pendientes")
async def listar_pendientes():
    """Bandeja del abogado: borradores aún sin decisión final."""
    repo = get_repository()
    pendientes = [
        d.to_dict()
        for d in repo.list_drafts()
        if d.estado in {ESTADO_PROPUESTO, "en_revision"}
    ]
    return {"drafts": pendientes}


@router.get("/drafts/{draft_id}")
async def obtener_borrador(draft_id: str):
    draft = get_repository().get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    return draft.to_dict()


def _aplicar(accion, draft_id: str, **kwargs):
    try:
        return accion(draft_id, **kwargs)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.") from exc
    except TransicionInvalida as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/drafts/{draft_id}/approve")
async def aprobar_borrador(draft_id: str, req: AprobarRequest):
    draft = _aplicar(hitl.aprobar, draft_id, revisor=req.revisor, comentario=req.comentario)
    termino = None
    # Al aprobar una tutela, registrar automáticamente el término de fallo (10 días hábiles).
    if draft.tipo == "tutela":
        from src.services.plazos import termino_fallo_tutela

        termino = get_repository().add_deadline(termino_fallo_tutela(draft.session_id))
    resultado = draft.to_dict()
    if termino is not None:
        resultado["termino_creado"] = termino.to_dict()
    return resultado


@router.post("/drafts/{draft_id}/reject")
async def rechazar_borrador(draft_id: str, req: RechazarRequest):
    draft = _aplicar(hitl.rechazar, draft_id, revisor=req.revisor, comentario=req.comentario)
    return draft.to_dict()


@router.post("/drafts/{draft_id}/edit")
async def editar_borrador(draft_id: str, req: EditarRequest):
    draft = _aplicar(
        hitl.editar, draft_id, revisor=req.revisor, nuevo_contenido=req.contenido, comentario=req.comentario
    )
    return draft.to_dict()


@router.get("/drafts/{draft_id}/docx")
async def descargar_docx(draft_id: str):
    draft = get_repository().get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    data = docx_desde_borrador(draft)
    filename = f"{draft.tipo}-{draft.id}.docx"
    return Response(
        content=data,
        media_type=_DOCX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/drafts/{draft_id}/pdf")
async def descargar_pdf(draft_id: str):
    draft = get_repository().get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    try:
        data = generar_pdf_desde_borrador(draft)
    except Exception as exc:  # WeasyPrint o libs de sistema ausentes
        raise HTTPException(status_code=503, detail=f"PDF no disponible: {exc}") from exc
    filename = f"{draft.tipo}-{draft.id}.pdf"
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/documents/extract")
async def extraer_documento(
    file: UploadFile = File(...),
    expediente_id: str | None = Form(default=None),
    ingestar: bool = Form(default=False),
):
    """Extrae texto de un adjunto y, opcionalmente, lo ingesta al RAG del expediente."""
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande (máx 10 MB).")
    try:
        texto = extraer_texto(file.filename or "", data)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    fragmentos = 0
    if ingestar:
        if not expediente_id:
            raise HTTPException(status_code=400, detail="Se requiere expediente_id para ingestar.")
        fragmentos = rag.ingestar_expediente(
            texto, expediente_id=expediente_id, fuente=file.filename or "adjunto"
        )
    return {
        "filename": file.filename,
        "caracteres": len(texto),
        "fragmentos_indexados": fragmentos,
        "texto": texto,
    }


class BuscarRequest(BaseModel):
    consulta: str
    expediente_id: str | None = None
    incluir_kb: bool = True
    k: int = 5


@router.post("/rag/search")
async def rag_search(req: BuscarRequest):
    """Búsqueda semántica (RAG) en la KB y/o documentos de un expediente."""
    chunks = rag.buscar(
        req.consulta,
        expediente_id=req.expediente_id,
        incluir_kb=req.incluir_kb,
        k=max(1, min(req.k, 20)),
    )
    return {"resultados": [c.to_dict() for c in chunks]}


@router.post("/rag/ingest-kb")
async def rag_ingest_kb(reindexar: bool = False):
    """Indexa la base de conocimiento curada (agente/conocimiento/*.md)."""
    resultados = rag.ingestar_kb_directorio(reindexar=reindexar)
    return {"indexados": resultados, "total_fragmentos": sum(resultados.values())}


@router.get("/deadlines")
async def listar_terminos(session_id: str | None = None, solo_pendientes: bool = False):
    items = get_repository().list_deadlines(session_id=session_id, solo_pendientes=solo_pendientes)
    return {"deadlines": [d.to_dict() for d in items]}


class CrearTerminoRequest(BaseModel):
    session_id: str
    descripcion: str
    dias_habiles: int
    tipo: str = "termino"
    fecha_base: date | None = None


@router.post("/deadlines")
async def crear_termino_endpoint(req: CrearTerminoRequest):
    if req.dias_habiles <= 0:
        raise HTTPException(status_code=400, detail="dias_habiles debe ser mayor a 0.")
    termino = crear_termino(
        session_id=req.session_id,
        descripcion=req.descripcion,
        dias_habiles=req.dias_habiles,
        tipo=req.tipo,
        fecha_base=req.fecha_base,
    )
    guardado = get_repository().add_deadline(termino)
    return guardado.to_dict()


class ActualizarTerminoRequest(BaseModel):
    estado: str  # pendiente | cumplido | vencido


@router.patch("/deadlines/{deadline_id}")
async def actualizar_termino(deadline_id: str, req: ActualizarTerminoRequest):
    if req.estado not in {"pendiente", "cumplido", "vencido"}:
        raise HTTPException(status_code=400, detail="estado inválido.")
    actualizado = get_repository().update_deadline(deadline_id, estado=req.estado)
    if actualizado is None:
        raise HTTPException(status_code=404, detail="Término no encontrado.")
    return actualizado.to_dict()
