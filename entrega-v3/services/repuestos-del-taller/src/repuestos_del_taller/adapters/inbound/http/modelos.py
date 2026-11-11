"""Modelos de solicitudes HTTP, autocontenidos y convertibles a comandos."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RegistrarEntradaDeRepuestoSolicitud:
    referencia: str; cantidad: int; stock_minimo: int; plazo_dias: int

@dataclass
class ReservarRepuestoSolicitud:
    referencia: str; orden_trabajo_id: str; cantidad: int

@dataclass
class LiberarReservaSolicitud:
    referencia: str; orden_trabajo_id: str

@dataclass
class ConfirmarConsumoSolicitud:
    referencia: str; orden_trabajo_id: str

@dataclass
class AjustarExistenciaPorConteoSolicitud:
    referencia: str; conteo: int

@dataclass
class SolicitarReposicionSolicitud:
    referencia: str; cantidad: int; monto: int; solicitud_id: str

@dataclass
class AprobarSolicitudSolicitud:
    solicitud_id: str

@dataclass
class CancelarSolicitudSolicitud:
    solicitud_id: str
