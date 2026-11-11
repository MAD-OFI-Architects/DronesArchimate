"""Composition root: único lugar que conoce todas las capas."""
from __future__ import annotations

import os
import re

from ....application.manejadores import (
    AprobarSolicitudManejador, AjustarExistenciaPorConteoManejador, CancelarSolicitudManejador,
    ConfirmarConsumoManejador, LiberarReservaManejador, RegistrarEntradaDeRepuestoManejador,
    ReservarRepuestoManejador, SolicitarReposicionManejador,
)
from ...outbound.persistencia import (
    RepositorioCacheadoExistencia, RepositorioCacheadoSolicitudDeReposicion,
    RepositorioExistencia, RepositorioExistenciaSql, RepositorioSolicitudDeReposicion,
    RepositorioSolicitudDeReposicionSql,
)
from ....application.traductores import FaltanteDetectadoTraductor
from ....application.integracion import (
    OrdenDeTrabajoCerradaConsumidor, ParadaProgramadaConsumidor, StockMinimoAlcanzadoObservador,
)
from ....adapters.outbound.integracion import (
    AlmacenDeBandejaEnMemoria, AlmacenDeBandejaSql, BandejaDeSalida, EnviarAvisoAdapter, ProcesadorDeMensajeEntrante,
    PublicadorConBandeja, PublicadorDeEventosHttp, RegistroDeProcesadosEnMemoria, RegistroDeProcesadosSql,
)
from ....adapters.outbound.seguridad import CifradorAes
from ....contracts.topicos import PlanDeMantenimientoTopicos, IntervencionesTopicos
from .endpoints import RepuestosDelTallerEndpoints


_DIALECTO_SQLALCHEMY = re.compile(r"^postgresql\+[a-z0-9_]+://")


def _dsn(database_url: str) -> str:
    """``psycopg`` solo acepta ``postgresql://``; el compose publica el DSN con el dialecto de SQLAlchemy."""
    return _DIALECTO_SQLALCHEMY.sub("postgresql://", database_url)


def _persistencia(database_url: str):
    """PostgreSQL cuando ``DATABASE_URL`` está definida (repositorios, outbox e inbox durables);
    memoria solo como alternativa explícita de test."""
    if not database_url:
        return RepositorioExistencia(), RepositorioSolicitudDeReposicion(), AlmacenDeBandejaEnMemoria(), RegistroDeProcesadosEnMemoria()
    import psycopg
    conexion = psycopg.connect(_dsn(database_url), autocommit=True)
    return (RepositorioExistenciaSql(conexion), RepositorioSolicitudDeReposicionSql(conexion),
            AlmacenDeBandejaSql(conexion), RegistroDeProcesadosSql(conexion))


class RepuestosDelTallerComposicion:
    def __init__(self, publicador=None, database_url: str | None = None) -> None:
        base_existencias, base_solicitudes, almacen_bandeja, registro = _persistencia(
            os.getenv("DATABASE_URL", "") if database_url is None else database_url)
        existencia = RepositorioCacheadoExistencia(base_existencias)
        solicitudes = RepositorioCacheadoSolicitudDeReposicion(base_solicitudes)
        procesador = ProcesadorDeMensajeEntrante(registro)
        if publicador is None:
            bandeja, bus = BandejaDeSalida(CifradorAes(), almacen_bandeja), PublicadorDeEventosHttp()
            bandeja.despachar(bus)  # reenvía lo que quedó pendiente antes del último reinicio
            publicador = PublicadorConBandeja(bandeja, bus)
        reservar = ReservarRepuestoManejador(existencia, publicador, FaltanteDetectadoTraductor())
        observador = StockMinimoAlcanzadoObservador(SolicitarReposicionManejador(solicitudes), aviso=EnviarAvisoAdapter())
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
