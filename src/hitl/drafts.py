"""Flujo de revisión humana (HITL) de borradores.

La IA propone; el abogado revisa y aprueba. Toda salida accionable se
materializa como un `Draft` que transita por una máquina de estados controlada.
"""

from __future__ import annotations

from src.storage import Repository, get_repository
from src.storage.models import (
    ESTADO_APROBADO,
    ESTADO_EDITADO,
    ESTADO_EN_REVISION,
    ESTADO_PROPUESTO,
    ESTADO_RECHAZADO,
    ESTADOS_FINALES,
    Draft,
)


class TransicionInvalida(ValueError):
    """Se intentó una transición de estado no permitida."""


# Transiciones permitidas en el flujo de aprobación.
_TRANSICIONES: dict[str, set[str]] = {
    ESTADO_PROPUESTO: {ESTADO_EN_REVISION, ESTADO_APROBADO, ESTADO_EDITADO, ESTADO_RECHAZADO},
    ESTADO_EN_REVISION: {ESTADO_APROBADO, ESTADO_EDITADO, ESTADO_RECHAZADO},
    ESTADO_APROBADO: set(),
    ESTADO_EDITADO: set(),
    ESTADO_RECHAZADO: set(),
}


def transicion_valida(actual: str, nuevo: str) -> bool:
    return nuevo in _TRANSICIONES.get(actual, set())


def _repo(repo: Repository | None) -> Repository:
    return repo or get_repository()


def crear_borrador(
    *,
    session_id: str,
    contenido: str,
    tipo: str = "documento",
    titulo: str = "",
    materia: str | None = None,
    repo: Repository | None = None,
) -> Draft:
    draft = Draft(
        session_id=session_id,
        tipo=tipo,
        titulo=titulo or tipo.capitalize(),
        contenido=contenido,
        materia=materia,
        estado=ESTADO_PROPUESTO,
    )
    return _repo(repo).add_draft(draft)


def _transicionar(
    draft_id: str,
    nuevo_estado: str,
    *,
    repo: Repository | None,
    **changes,
) -> Draft:
    repository = _repo(repo)
    draft = repository.get_draft(draft_id)
    if draft is None:
        raise KeyError(f"Borrador no encontrado: {draft_id}")
    if draft.estado == nuevo_estado:
        return draft
    if not transicion_valida(draft.estado, nuevo_estado):
        raise TransicionInvalida(
            f"No se puede pasar de '{draft.estado}' a '{nuevo_estado}'."
        )
    updated = repository.update_draft(draft_id, estado=nuevo_estado, **changes)
    assert updated is not None
    return updated


def enviar_a_revision(draft_id: str, *, slack_ts: str | None = None, repo: Repository | None = None) -> Draft:
    changes = {"slack_ts": slack_ts} if slack_ts is not None else {}
    return _transicionar(draft_id, ESTADO_EN_REVISION, repo=repo, **changes)


def aprobar(draft_id: str, *, revisor: str, comentario: str | None = None, repo: Repository | None = None) -> Draft:
    return _transicionar(
        draft_id, ESTADO_APROBADO, repo=repo, revisor=revisor, comentario=comentario
    )


def editar(
    draft_id: str,
    *,
    revisor: str,
    nuevo_contenido: str,
    comentario: str | None = None,
    repo: Repository | None = None,
) -> Draft:
    return _transicionar(
        draft_id,
        ESTADO_EDITADO,
        repo=repo,
        revisor=revisor,
        contenido=nuevo_contenido,
        comentario=comentario,
    )


def rechazar(draft_id: str, *, revisor: str, comentario: str, repo: Repository | None = None) -> Draft:
    return _transicionar(
        draft_id, ESTADO_RECHAZADO, repo=repo, revisor=revisor, comentario=comentario
    )


def es_final(draft: Draft) -> bool:
    return draft.estado in ESTADOS_FINALES
