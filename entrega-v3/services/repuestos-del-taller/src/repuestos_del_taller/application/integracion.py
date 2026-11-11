"""Traducción de eventos y consumidores idempotentes del bus."""
from __future__ import annotations

from typing import Any, Callable

from ..contracts.eventos import FaltanteDetectadoV1
from ..domain.existencias.eventos import FaltanteDetectado, StockMinimoAlcanzado
from ..domain.compartido.eventos import EventoDeDominio
from ..domain.compartido.errores import ViolacionDeReglaDeNegocio
from .comandos import (
    ConfirmarConsumoComando, ReservarRepuestoComando, SolicitarReposicionComando,
)
from .manejadores import (
    ConfirmarConsumoManejador, ReservarRepuestoManejador,
    SolicitarReposicionManejador,
)


class FaltanteDetectadoTraductor:
    def traducir(self, evento: FaltanteDetectado) -> FaltanteDetectadoV1:
        return FaltanteDetectadoV1(
            event_id=str(evento.evento_id), occurred_on=evento.ocurrio_en.isoformat(),
            parada_id=evento.orden_trabajo_id, referencia=evento.referencia,
            cantidad_faltante=max(0, evento.solicitada - evento.disponible),
        )


class _ConsumidorIdempotente:
    def __init__(self) -> None:
        self._procesados: set[str] = set()

    def _una_vez(self, envelope: dict[str, Any], accion: Callable[[], None]) -> bool:
        event_id = str(envelope.get("eventId", ""))
        if not event_id or event_id in self._procesados:
            return False
        accion(); self._procesados.add(event_id); return True


class ParadaProgramadaConsumidor(_ConsumidorIdempotente):
    def __init__(self, manejador: ReservarRepuestoManejador) -> None:
        super().__init__(); self.manejador = manejador

    def consumir(self, envelope: dict[str, Any]) -> bool:
        payload = envelope.get("payload", {})
        def procesar() -> None:
            for tarea in payload.get("tareas", []):
                for repuesto in tarea.get("repuestos", []):
                    self._reservar(repuesto, str(payload.get("paradaId", "")))
        return self._una_vez(envelope, procesar)

    def _reservar(self, repuesto: dict[str, Any], parada_id: str) -> None:
        try:
            self.manejador.manejar(ReservarRepuestoComando(
                referencia=repuesto["referencia"], orden_trabajo_id=parada_id, cantidad=repuesto["cantidad"],
            ))
        except ViolacionDeReglaDeNegocio:
            pass  # el manejador ya publicó Faltante detectado; reintentar el sobre lo duplicaría


class OrdenDeTrabajoCerradaConsumidor(_ConsumidorIdempotente):
    def __init__(self, manejador: ConfirmarConsumoManejador) -> None:
        super().__init__(); self.manejador = manejador

    def consumir(self, envelope: dict[str, Any]) -> bool:
        payload = envelope.get("payload", {})
        def procesar() -> None:
            for consumo in payload.get("consumos", []):
                self.manejador.manejar(ConfirmarConsumoComando(
                    referencia=consumo["referencia"],
                    orden_trabajo_id=str(payload.get("paradaId") or payload.get("ordenId", "")),
                ))
        return self._una_vez(envelope, procesar)


class StockMinimoAlcanzadoObservador:
    def __init__(self, manejador: SolicitarReposicionManejador, cantidad: int = 1, monto: int = 0) -> None:
        self.manejador = manejador; self.cantidad = cantidad; self.monto = monto

    def observar(self, evento: StockMinimoAlcanzado, solicitud_id: str) -> None:
        try:
            self.manejador.manejar(SolicitarReposicionComando(
                referencia=evento.referencia, cantidad=self.cantidad,
                monto=self.monto, solicitud_id=solicitud_id,
            ))
        except ViolacionDeReglaDeNegocio:
            pass  # ya hay una solicitud abierta para la referencia: no se duplica
