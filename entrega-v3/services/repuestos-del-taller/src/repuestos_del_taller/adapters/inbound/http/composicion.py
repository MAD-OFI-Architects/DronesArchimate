"""Composition root: único lugar que conoce todas las capas."""
from __future__ import annotations

from ....application.manejadores import (
    AprobarSolicitudManejador, AjustarExistenciaPorConteoManejador, CancelarSolicitudManejador,
    ConfirmarConsumoManejador, LiberarReservaManejador, RegistrarEntradaDeRepuestoManejador,
    ReservarRepuestoManejador, SolicitarReposicionManejador,
)
from ...outbound.persistencia import (
    RepositorioCacheadoExistencia, RepositorioCacheadoSolicitudDeReposicion,
    RepositorioExistencia, RepositorioSolicitudDeReposicion,
)
from ....application.integracion import (
    OrdenDeTrabajoCerradaConsumidor, ParadaProgramadaConsumidor, StockMinimoAlcanzadoObservador,
)
from ....adapters.outbound.integracion import ProcesadorDeMensajeEntrante, PublicadorDeEventosHttp
from ....contracts.topicos import PlanDeMantenimientoTopicos, IntervencionesTopicos
from .endpoints import RepuestosDelTallerEndpoints


class RepuestosDelTallerComposicion:
    def __init__(self, publicador=None) -> None:
        existencia = RepositorioCacheadoExistencia(RepositorioExistencia())
        solicitudes = RepositorioCacheadoSolicitudDeReposicion(RepositorioSolicitudDeReposicion())
        procesador = ProcesadorDeMensajeEntrante()
        publicador = publicador or PublicadorDeEventosHttp()
        reservar = ReservarRepuestoManejador(existencia, publicador)
        observador = StockMinimoAlcanzadoObservador(SolicitarReposicionManejador(solicitudes))
        confirmar = ConfirmarConsumoManejador(existencia, observador)
        consumidores = {
            PlanDeMantenimientoTopicos.PARADA_PROGRAMADA: ParadaProgramadaConsumidor(reservar),
            IntervencionesTopicos.ORDEN_DE_TRABAJO_CERRADA: OrdenDeTrabajoCerradaConsumidor(confirmar),
        }
        self.endpoints = RepuestosDelTallerEndpoints(
            RegistrarEntradaDeRepuestoManejador(existencia), reservar,
            LiberarReservaManejador(existencia), confirmar,
            AjustarExistenciaPorConteoManejador(existencia), SolicitarReposicionManejador(solicitudes),
            AprobarSolicitudManejador(solicitudes, existencia), CancelarSolicitudManejador(solicitudes),
            existencia, solicitudes, procesador, consumidores,
        )

    def crear_app(self):
        return self.endpoints.crear_app()


app = RepuestosDelTallerComposicion().crear_app()
