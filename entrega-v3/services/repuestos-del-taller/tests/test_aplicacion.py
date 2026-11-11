"""Casos de uso, validadores, traductor y consumidores con adaptadores en memoria."""
import uuid

import pytest

from repuestos_del_taller.adapters.outbound.persistencia import RepositorioExistencia, RepositorioSolicitudDeReposicion
from repuestos_del_taller.application.comandos import (
    AjustarExistenciaPorConteoComando, AprobarSolicitudComando, CancelarSolicitudComando,
    ConfirmarConsumoComando, LiberarReservaComando, RegistrarEntradaDeRepuestoComando,
    ReservarRepuestoComando, SolicitarReposicionComando,
)
from repuestos_del_taller.application.integracion import (
    OrdenDeTrabajoCerradaConsumidor, ParadaProgramadaConsumidor, StockMinimoAlcanzadoObservador,
)
from repuestos_del_taller.application.manejadores import (
    AjustarExistenciaPorConteoManejador, AprobarSolicitudManejador, CancelarSolicitudManejador,
    ConfirmarConsumoManejador, LiberarReservaManejador, RegistrarEntradaDeRepuestoManejador,
    ReservarRepuestoManejador, SolicitarReposicionManejador,
)
from repuestos_del_taller.application.puertos import IPublicadorDeEventos
from repuestos_del_taller.application.traductores import FaltanteDetectadoTraductor
from repuestos_del_taller.application.validadores import (
    AjustarExistenciaPorConteoValidador, AprobarSolicitudValidador, CancelarSolicitudValidador,
    ConfirmarConsumoValidador, LiberarReservaValidador, RegistrarEntradaDeRepuestoValidador,
    ReservarRepuestoValidador, SolicitarReposicionValidador,
)
from repuestos_del_taller.contracts.topicos import RepuestosDelTallerTopicos
from repuestos_del_taller.domain.existencias.eventos import FaltanteDetectado
from repuestos_del_taller.domain.existencias.objetos_de_valor import Cantidad
from repuestos_del_taller.domain.compartido.errores import ViolacionDeReglaDeNegocio


class BandejaEnMemoria(IPublicadorDeEventos):
    def __init__(self): self.eventos = []
    def publicar(self, topico, payload): self.eventos.append((topico, payload))


@pytest.fixture
def existencias():
    repo = RepositorioExistencia()
    RegistrarEntradaDeRepuestoManejador(repo).manejar(RegistrarEntradaDeRepuestoComando("R-1", 4, 1, 2))
    return repo


@pytest.fixture
def solicitudes():
    return RepositorioSolicitudDeReposicion()


def _solicitar(solicitudes, referencia="R-1"):
    sid = str(uuid.uuid4())
    SolicitarReposicionManejador(solicitudes).manejar(SolicitarReposicionComando(referencia, 3, 100, sid))
    return uuid.UUID(sid)


def test_registrar_entrada_persiste_y_acumula(existencias):
    RegistrarEntradaDeRepuestoManejador(existencias).manejar(RegistrarEntradaDeRepuestoComando("R-1", 2, 1, 2))
    assert existencias.por_referencia("R-1").fisica.valor == 6


def test_reservar_persiste_la_reserva(existencias):
    bandeja = BandejaEnMemoria()
    ReservarRepuestoManejador(existencias, bandeja).manejar(ReservarRepuestoComando("R-1", "OT-1", 3))
    assert existencias.por_referencia("R-1").reservada == 3 and bandeja.eventos == []


def test_reservar_sin_existencia_escribe_faltante_en_la_bandeja(existencias):
    bandeja = BandejaEnMemoria()
    with pytest.raises(ViolacionDeReglaDeNegocio):
        ReservarRepuestoManejador(existencias, bandeja).manejar(ReservarRepuestoComando("R-1", "OT-9", 6))
    (topico, payload), = bandeja.eventos
    assert topico == RepuestosDelTallerTopicos.FALTANTE_DETECTADO
    assert (payload["paradaId"], payload["referencia"], payload["cantidadFaltante"]) == ("OT-9", "R-1", 2)
    assert payload["eventId"] and existencias.por_referencia("R-1").eventos == ()


def test_liberar_reserva_devuelve_el_stock(existencias):
    ReservarRepuestoManejador(existencias).manejar(ReservarRepuestoComando("R-1", "OT-1", 3))
    LiberarReservaManejador(existencias).manejar(LiberarReservaComando("R-1", "OT-1"))
    assert existencias.por_referencia("R-1").reservada == 0


def test_confirmar_consumo_descuenta_existencia_fisica(existencias):
    ReservarRepuestoManejador(existencias).manejar(ReservarRepuestoComando("R-1", "OT-1", 2))
    ConfirmarConsumoManejador(existencias).manejar(ConfirmarConsumoComando("R-1", "OT-1"))
    assert existencias.por_referencia("R-1").fisica.valor == 2


def test_ajustar_por_conteo_fija_la_existencia(existencias):
    AjustarExistenciaPorConteoManejador(existencias).manejar(AjustarExistenciaPorConteoComando("R-1", 7))
    assert existencias.por_referencia("R-1").fisica.valor == 7


def test_solicitar_reposicion_persiste_solicitud_abierta(solicitudes):
    sid = _solicitar(solicitudes)
    assert solicitudes.por_id(sid).estado == "abierta"


def test_solicitar_reposicion_rechaza_segunda_abierta_de_la_misma_referencia(solicitudes):
    _solicitar(solicitudes)
    with pytest.raises(ViolacionDeReglaDeNegocio):
        _solicitar(solicitudes)


def test_aprobar_y_cancelar_solicitud(solicitudes, existencias):
    aprobada, cancelada = _solicitar(solicitudes, "R-1"), _solicitar(solicitudes, "R-2")
    AprobarSolicitudManejador(solicitudes, existencias).manejar(AprobarSolicitudComando(str(aprobada)))
    CancelarSolicitudManejador(solicitudes).manejar(CancelarSolicitudComando(str(cancelada)))
    assert solicitudes.por_id(aprobada).estado == "aprobada" and solicitudes.por_id(cancelada).estado == "cancelada"


@pytest.mark.parametrize("manejador, comando", [
    (lambda e, s: RegistrarEntradaDeRepuestoManejador(e), RegistrarEntradaDeRepuestoComando("", 1, 1, 1)),
    (lambda e, s: ReservarRepuestoManejador(e), ReservarRepuestoComando("R-1", "OT", 0)),
    (lambda e, s: LiberarReservaManejador(e), LiberarReservaComando("R-1", " ")),
    (lambda e, s: ConfirmarConsumoManejador(e), ConfirmarConsumoComando("", "OT")),
    (lambda e, s: AjustarExistenciaPorConteoManejador(e), AjustarExistenciaPorConteoComando("R-1", -1)),
    (lambda e, s: SolicitarReposicionManejador(s), SolicitarReposicionComando("R-1", 0, 1, "x")),
    (lambda e, s: AprobarSolicitudManejador(s), AprobarSolicitudComando("")),
    (lambda e, s: CancelarSolicitudManejador(s), CancelarSolicitudComando(" ")),
])
def test_comando_invalido_es_rechazado_sin_tocar_el_estado(manejador, comando, existencias, solicitudes):
    with pytest.raises(ValueError):
        manejador(existencias, solicitudes).manejar(comando)
    assert existencias.por_referencia("R-1").fisica.valor == 4 and solicitudes.abierta_de_referencia("R-1") is None


@pytest.mark.parametrize("validador, comando", [
    (RegistrarEntradaDeRepuestoValidador, RegistrarEntradaDeRepuestoComando("R", 1, 0, 0)),
    (ReservarRepuestoValidador, ReservarRepuestoComando("R", "OT", 1)),
    (LiberarReservaValidador, LiberarReservaComando("R", "OT")),
    (ConfirmarConsumoValidador, ConfirmarConsumoComando("R", "OT")),
    (AjustarExistenciaPorConteoValidador, AjustarExistenciaPorConteoComando("R", 0)),
    (SolicitarReposicionValidador, SolicitarReposicionComando("R", 1, 0, "id")),
    (AprobarSolicitudValidador, AprobarSolicitudComando("id")),
    (CancelarSolicitudValidador, CancelarSolicitudComando("id")),
])
def test_validador_acepta_su_comando_y_rechaza_otro_tipo(validador, comando):
    validador().validar(comando)
    with pytest.raises(TypeError):
        validador().validar(object())


def test_traductor_conserva_el_id_del_evento(existencias):
    existencia = existencias.por_referencia("R-1")
    with pytest.raises(ViolacionDeReglaDeNegocio):
        existencia.reservar("OT-9", Cantidad(9))
    evento = next(e for e in existencia.eventos if isinstance(e, FaltanteDetectado))
    v1 = FaltanteDetectadoTraductor().traducir(evento)
    assert v1.event_id == str(evento.evento_id) and v1.cantidad_faltante == 5 and v1.parada_id == "OT-9"


def _parada(event_id, cantidad):
    return {"eventId": event_id, "payload": {"paradaId": "P-1", "tareas": [{"repuestos": [{"referencia": "R-1", "cantidad": cantidad}]}]}}


def test_parada_programada_reserva_y_es_idempotente(existencias):
    consumidor = ParadaProgramadaConsumidor(ReservarRepuestoManejador(existencias))
    assert consumidor.consumir(_parada("e-1", 2)) is True
    assert consumidor.consumir(_parada("e-1", 2)) is False
    assert existencias.por_referencia("R-1").reservada == 2


def test_orden_cerrada_confirma_consumo_y_es_idempotente(existencias):
    ReservarRepuestoManejador(existencias).manejar(ReservarRepuestoComando("R-1", "P-1", 2))
    consumidor = OrdenDeTrabajoCerradaConsumidor(ConfirmarConsumoManejador(existencias))
    sobre = {"eventId": "e-2", "payload": {"paradaId": "P-1", "consumos": [{"referencia": "R-1", "cantidad": 2}]}}
    assert consumidor.consumir(sobre) is True and consumidor.consumir(sobre) is False
    assert existencias.por_referencia("R-1").fisica.valor == 2


def test_observador_despacha_solicitar_reposicion_al_llegar_al_minimo(existencias, solicitudes):
    ReservarRepuestoManejador(existencias).manejar(ReservarRepuestoComando("R-1", "OT-1", 3))
    observador = StockMinimoAlcanzadoObservador(SolicitarReposicionManejador(solicitudes))
    ConfirmarConsumoManejador(existencias, observador).manejar(ConfirmarConsumoComando("R-1", "OT-1"))
    assert solicitudes.abierta_de_referencia("R-1") is not None
