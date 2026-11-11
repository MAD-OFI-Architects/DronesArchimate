"""Manejadores: orquestan repositorios, dominio y eventos pendientes."""
from __future__ import annotations

import uuid

from ..domain.existencias.eventos import StockMinimoAlcanzado
from ..domain.existencias.existencia import Existencia
from ..domain.existencias.objetos_de_valor import Cantidad, PlazoDeEntrega, StockMinimo
from ..domain.existencias.repositorio import IExistenciaRepository
from ..domain.compartido.errores import ViolacionDeReglaDeNegocio
from ..domain.reposicion.objetos_de_valor import CantidadSolicitada
from ..domain.reposicion.repositorio import ISolicitudDeReposicionRepository
from ..domain.reposicion.solicitud_de_reposicion import SolicitudDeReposicion
from ..domain.existencias.eventos import FaltanteDetectado
from .comandos import (
    AjustarExistenciaPorConteoComando, AprobarSolicitudComando, CancelarSolicitudComando,
    ConfirmarConsumoComando, LiberarReservaComando, RegistrarEntradaDeRepuestoComando,
    ReservarRepuestoComando, SolicitarReposicionComando,
)
from .puertos import IPublicadorDeEventos
from .traductores import FaltanteDetectadoTraductor
from .validadores import (
    AjustarExistenciaPorConteoValidador, AprobarSolicitudValidador, CancelarSolicitudValidador,
    ConfirmarConsumoValidador, LiberarReservaValidador, RegistrarEntradaDeRepuestoValidador,
    ReservarRepuestoValidador, SolicitarReposicionValidador,
)
from ..contracts.topicos import RepuestosDelTallerTopicos


class RegistrarEntradaDeRepuestoManejador:
    def __init__(self, repositorio: IExistenciaRepository): self.repositorio = repositorio
    def manejar(self, comando: RegistrarEntradaDeRepuestoComando) -> Existencia:
        RegistrarEntradaDeRepuestoValidador().validar(comando)
        existencia = self.repositorio.por_referencia(comando.referencia)
        if existencia is None:
            existencia = Existencia.registrar_entrada(comando.referencia, Cantidad(comando.cantidad), StockMinimo(comando.stock_minimo), PlazoDeEntrega(comando.plazo_dias))
        else: existencia.recibir(Cantidad(comando.cantidad))
        self.repositorio.guardar(existencia); return existencia


class ReservarRepuestoManejador:
    def __init__(self, repositorio: IExistenciaRepository, publicador: IPublicadorDeEventos | None = None,
                 traductor: FaltanteDetectadoTraductor | None = None):
        self.repositorio = repositorio; self.publicador = publicador
        self.traductor = traductor or FaltanteDetectadoTraductor()
    def manejar(self, comando: ReservarRepuestoComando) -> Existencia:
        ReservarRepuestoValidador().validar(comando); e = self.repositorio.por_referencia(comando.referencia)
        if e is None: raise LookupError("REFERENCIA_INEXISTENTE")
        try:
            e.reservar(comando.orden_trabajo_id, Cantidad(comando.cantidad))
        except ViolacionDeReglaDeNegocio:
            self.repositorio.guardar(e)
            self._escribir_en_bandeja(e)
            raise
        self.repositorio.guardar(e); self._escribir_en_bandeja(e); return e

    def _escribir_en_bandeja(self, existencia: Existencia) -> None:
        for evento in existencia.eventos:
            if isinstance(evento, FaltanteDetectado) and self.publicador:
                self.publicador.publicar(
                    RepuestosDelTallerTopicos.FALTANTE_DETECTADO, self.traductor.traducir(evento).a_payload())
        existencia.limpiar_eventos()


class LiberarReservaManejador:
    def __init__(self, repositorio: IExistenciaRepository): self.repositorio = repositorio
    def manejar(self, comando: LiberarReservaComando) -> Existencia:
        LiberarReservaValidador().validar(comando); e = self.repositorio.por_referencia(comando.referencia)
        if e is None: raise LookupError("REFERENCIA_INEXISTENTE")
        e.liberar_reserva(comando.orden_trabajo_id); self.repositorio.guardar(e); return e


class ConfirmarConsumoManejador:
    def __init__(self, repositorio: IExistenciaRepository, observador=None):
        self.repositorio = repositorio; self.observador = observador
    def manejar(self, comando: ConfirmarConsumoComando) -> Existencia:
        ConfirmarConsumoValidador().validar(comando); e = self.repositorio.por_referencia(comando.referencia)
        if e is None: raise LookupError("REFERENCIA_INEXISTENTE")
        e.confirmar_consumo(comando.orden_trabajo_id); self.repositorio.guardar(e)
        self._notificar_stock_minimo(e); return e

    def _notificar_stock_minimo(self, existencia: Existencia) -> None:
        if self.observador:
            for evento in existencia.eventos:
                if isinstance(evento, StockMinimoAlcanzado):
                    self.observador.observar(evento, str(uuid.uuid4()))
        existencia.limpiar_eventos()


class AjustarExistenciaPorConteoManejador:
    def __init__(self, repositorio: IExistenciaRepository): self.repositorio = repositorio
    def manejar(self, comando: AjustarExistenciaPorConteoComando) -> Existencia:
        AjustarExistenciaPorConteoValidador().validar(comando); e = self.repositorio.por_referencia(comando.referencia)
        if e is None: raise LookupError("REFERENCIA_INEXISTENTE")
        e.ajustar_existencia_por_conteo(Cantidad(comando.conteo)); self.repositorio.guardar(e); return e


class SolicitarReposicionManejador:
    def __init__(self, repositorio: ISolicitudDeReposicionRepository): self.repositorio = repositorio
    def manejar(self, comando: SolicitarReposicionComando) -> SolicitudDeReposicion:
        SolicitarReposicionValidador().validar(comando)
        abierta = self.repositorio.abierta_de_referencia(comando.referencia) is not None
        s = SolicitudDeReposicion.solicitar(uuid.UUID(comando.solicitud_id), comando.referencia, CantidadSolicitada(comando.cantidad), comando.monto, abierta)
        self.repositorio.guardar(s); return s


class AprobarSolicitudManejador:
    def __init__(self, repositorio: ISolicitudDeReposicionRepository, existencias: IExistenciaRepository | None = None):
        self.repositorio = repositorio; self.existencias = existencias
    def manejar(self, comando: AprobarSolicitudComando) -> SolicitudDeReposicion:
        AprobarSolicitudValidador().validar(comando); s = self.repositorio.por_id(uuid.UUID(comando.solicitud_id))
        if s is None: raise LookupError("SOLICITUD_INEXISTENTE")
        s.aprobar(); self.repositorio.guardar(s); self._iniciar_reposicion(s.referencia); return s

    def _iniciar_reposicion(self, referencia: str) -> None:
        existencia = self.existencias.por_referencia(referencia) if self.existencias else None
        if existencia is not None and existencia.estado == "bajo_minimo":
            existencia.iniciar_reposicion(); self.existencias.guardar(existencia)


class CancelarSolicitudManejador:
    def __init__(self, repositorio: ISolicitudDeReposicionRepository): self.repositorio = repositorio
    def manejar(self, comando: CancelarSolicitudComando) -> SolicitudDeReposicion:
        CancelarSolicitudValidador().validar(comando); s = self.repositorio.por_id(uuid.UUID(comando.solicitud_id))
        if s is None: raise LookupError("SOLICITUD_INEXISTENTE")
        s.cancelar(); self.repositorio.guardar(s); return s
