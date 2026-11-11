"""Eventos de dominio del agregado «Solicitud de reposición» (inmutables)."""
from __future__ import annotations

from dataclasses import dataclass

from ..compartido.eventos import EventoDeDominio


@dataclass(frozen=True, kw_only=True)
class ReposicionSolicitada(EventoDeDominio):
    """El taller pidió reposición de una referencia."""

    solicitud_id: str
    referencia: str
    cantidad: int
    nivel: str


@dataclass(frozen=True, kw_only=True)
class SolicitudAprobada(EventoDeDominio):
    """La solicitud quedó aprobada por su nivel de aprobación."""

    solicitud_id: str
    referencia: str
    nivel: str


@dataclass(frozen=True, kw_only=True)
class SolicitudCancelada(EventoDeDominio):
    """La solicitud quedó cancelada."""

    solicitud_id: str
    referencia: str
