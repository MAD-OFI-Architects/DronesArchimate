"""Comandos inmutables: únicamente datos primitivos que entran a la aplicación."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegistrarEntradaDeRepuestoComando:
    referencia: str
    cantidad: int
    stock_minimo: int
    plazo_dias: int


@dataclass(frozen=True, slots=True)
class ReservarRepuestoComando:
    referencia: str
    orden_trabajo_id: str
    cantidad: int


@dataclass(frozen=True, slots=True)
class LiberarReservaComando:
    referencia: str
    orden_trabajo_id: str


@dataclass(frozen=True, slots=True)
class ConfirmarConsumoComando:
    referencia: str
    orden_trabajo_id: str


@dataclass(frozen=True, slots=True)
class AjustarExistenciaPorConteoComando:
    referencia: str
    conteo: int


@dataclass(frozen=True, slots=True)
class SolicitarReposicionComando:
    referencia: str
    cantidad: int
    monto: int
    solicitud_id: str


@dataclass(frozen=True, slots=True)
class AprobarSolicitudComando:
    solicitud_id: str


@dataclass(frozen=True, slots=True)
class CancelarSolicitudComando:
    solicitud_id: str
