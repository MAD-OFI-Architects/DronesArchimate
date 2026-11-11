"""Memento del agregado «Solicitud de reposición»: instantánea de primitivos."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SolicitudDeReposicionMemento:
    """Instantánea del agregado «Solicitud de reposición» para persistir."""

    id: str
    referencia: str
    cantidad_solicitada: int
    monto: int
    nivel: str
    estado: str
