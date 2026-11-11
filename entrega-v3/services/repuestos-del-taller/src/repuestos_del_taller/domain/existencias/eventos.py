"""Eventos de dominio del agregado «Existencia» (inmutables)."""
from __future__ import annotations

from dataclasses import dataclass

from ..compartido.eventos import EventoDeDominio


@dataclass(frozen=True, kw_only=True)
class RepuestoRecibido(EventoDeDominio):
    """Entrada de repuesto registrada por el almacenista."""

    referencia: str
    cantidad: int
    fisica: int
    plazo_dias: int


@dataclass(frozen=True, kw_only=True)
class RepuestoReservado(EventoDeDominio):
    """Se apartó repuesto para una orden de trabajo."""

    referencia: str
    orden_trabajo_id: str
    cantidad: int
    reservada: int


@dataclass(frozen=True, kw_only=True)
class FaltanteDetectado(EventoDeDominio):
    """No se pudo reservar: la orden de trabajo debe esperar."""

    referencia: str
    orden_trabajo_id: str
    solicitada: int
    disponible: int


@dataclass(frozen=True, kw_only=True)
class ReservaLiberada(EventoDeDominio):
    """El almacenista liberó el apartado de una orden de trabajo."""

    referencia: str
    orden_trabajo_id: str
    cantidad: int


@dataclass(frozen=True, kw_only=True)
class ConsumoConfirmado(EventoDeDominio):
    """Una orden de trabajo cerrada consumió su reserva."""

    referencia: str
    orden_trabajo_id: str
    cantidad: int


@dataclass(frozen=True, kw_only=True)
class StockMinimoAlcanzado(EventoDeDominio):
    """La existencia usable quedó en el stock mínimo o por debajo: se pide
    reposición inmediata."""

    referencia: str
    disponible: int
    stock_minimo: int


@dataclass(frozen=True, kw_only=True)
class ExistenciaAjustada(EventoDeDominio):
    """El conteo físico ajustó la cantidad de la referencia."""

    referencia: str
    fisica_anterior: int
    fisica_nueva: int
