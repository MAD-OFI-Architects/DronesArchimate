"""Memento del agregado «Existencia»: instantánea inmutable de primitivos."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReservaDeRepuestoMemento:
    """Instantánea de una reserva interna del agregado."""

    id: str
    orden_trabajo_id: str
    cantidad: int


@dataclass(frozen=True, slots=True)
class ExistenciaMemento:
    """Instantánea del agregado «Existencia» para persistir y reconstruir."""

    referencia: str
    fisica: int
    stock_minimo: int
    plazo_dias: int
    estado: str
    reservas: tuple[ReservaDeRepuestoMemento, ...]
