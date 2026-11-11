"""Traducción de eventos y consumidores idempotentes del bus."""
from __future__ import annotations

from typing import Any, Callable

from ..domain.existencias.eventos import StockMinimoAlcanzado
from ..domain.compartido.errores import ErrorDeDominio, ViolacionDeReglaDeNegocio
from .comandos import (
    ConfirmarConsumoComando, ReservarRepuestoComando, SolicitarReposicionComando,
)
from .puertos import IEnviarAviso
from .manejadores import (
    ConfirmarConsumoManejador, ReservarRepuestoManejador,
    SolicitarReposicionManejador,
)


class ParadaProgramadaConsumidor:
    """Reserva idempotente por (referencia, orden): reprocesar el mismo evento no duplica reservas.
    La deduplicación del evento vive en ProcesadorDeMensajeEntrante."""
    def __init__(self, manejador: ReservarRepuestoManejador) -> None:
        self.manejador = manejador

    def consumir(self, envelope: dict[str, Any]) -> bool:
        payload = envelope.get("payload", {})
        for tarea in payload.get("tareas", []):
            for repuesto in tarea.get("repuestos", []):
                self._reservar(repuesto, str(payload.get("paradaId", "")))
        return True

    def _reservar(self, repuesto: dict[str, Any], parada_id: str) -> None:
        try:
            self.manejador.manejar(ReservarRepuestoComando(
                referencia=repuesto["referencia"], orden_trabajo_id=parada_id, cantidad=repuesto["cantidad"],
            ))
        except ViolacionDeReglaDeNegocio:
            pass  # el manejador ya publicó Faltante detectado; reintentar el sobre lo duplicaría


class OrdenDeTrabajoCerradaConsumidor:
    """Confirma cada consumo; si un reintento encuentra uno ya confirmado (sin reserva), lo salta."""
    def __init__(self, manejador: ConfirmarConsumoManejador) -> None:
        self.manejador = manejador

    def consumir(self, envelope: dict[str, Any]) -> bool:
        payload = envelope.get("payload", {})
        for consumo in payload.get("consumos", []):
            try:
                self.manejador.manejar(ConfirmarConsumoComando(
                    referencia=consumo["referencia"],
                    orden_trabajo_id=str(payload.get("paradaId") or payload.get("ordenId", "")),
                ))
            except ErrorDeDominio:
                pass  # ya confirmado en un intento anterior del mismo evento
        return True


class StockMinimoAlcanzadoObservador:
    def __init__(self, manejador: SolicitarReposicionManejador, cantidad: int = 1, monto: int = 0,
                 aviso: IEnviarAviso | None = None, destinatario: str = "compras") -> None:
        self.manejador = manejador; self.cantidad = cantidad; self.monto = monto
        self.aviso = aviso; self.destinatario = destinatario

    def observar(self, evento: StockMinimoAlcanzado, solicitud_id: str) -> None:
        try:
            self.manejador.manejar(SolicitarReposicionComando(
                referencia=evento.referencia, cantidad=self.cantidad,
                monto=self.monto, solicitud_id=solicitud_id,
            ))
        except ViolacionDeReglaDeNegocio:
            pass  # ya hay una solicitud abierta para la referencia: no se duplica
        else:
            self._avisar(evento)

    def _avisar(self, evento: StockMinimoAlcanzado) -> None:
        if self.aviso is None:
            return
        try:
            self.aviso.enviar(self.destinatario, "Reposición solicitada", f"Stock mínimo alcanzado: {evento.referencia}")
        except OSError:
            pass  # el aviso es un efecto posterior: su fallo no revierte la solicitud
