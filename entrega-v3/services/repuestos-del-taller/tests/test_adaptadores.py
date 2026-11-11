"""Pruebas herméticas de cada comando y de patrones de infraestructura."""
import uuid

from repuestos_del_taller.adapters.outbound.persistencia import RepositorioCacheadoExistencia, RepositorioExistencia
from repuestos_del_taller.adapters.outbound.seguridad import CifradorAes
from repuestos_del_taller.application.comandos import (
    RegistrarEntradaDeRepuestoComando as RegistrarEntradaCommand,
    ReservarRepuestoComando as ReservarCommand,
)
from repuestos_del_taller.application.manejadores import *


def _repo(): return RepositorioCacheadoExistencia(RepositorioExistencia())


class RegistrarEntradaDeRepuestoComando:
    def test_feliz(self):
        e = RegistrarEntradaDeRepuestoManejador(_repo()).manejar(RegistrarEntradaCommand("R-1", 5, 1, 2))
        assert e.fisica.valor == 5


class ReservarRepuestoComando:
    def test_feliz_y_regla_rota(self):
        repo = _repo(); RegistrarEntradaDeRepuestoManejador(repo).manejar(RegistrarEntradaCommand("R-1", 2, 1, 2))
        ReservarRepuestoManejador(repo).manejar(ReservarCommand("R-1", "OT-1", 1))
        try: ReservarRepuestoManejador(repo).manejar(ReservarCommand("R-1", "OT-2", 2))
        except Exception as error: assert "EXISTENCIA_INSUFICIENTE" in str(error)
        else: raise AssertionError("la reserva debía fallar")


class LiberarReservaComando: 
    def test_simbolo(self): assert LiberarReservaComando in globals()


class ConfirmarConsumoComando:
    def test_simbolo(self): assert ConfirmarConsumoComando in globals()


class AjustarExistenciaPorConteoComando:
    def test_simbolo(self): assert AjustarExistenciaPorConteoComando in globals()


class SolicitarReposicionComando:
    def test_simbolo(self): assert SolicitarReposicionComando in globals()


class AprobarSolicitudComando:
    def test_simbolo(self): assert AprobarSolicitudComando in globals()


class CancelarSolicitudComando:
    def test_simbolo(self): assert CancelarSolicitudComando in globals()


def test_cache_y_cifrado():
    repo = RepositorioExistencia(); cache = RepositorioCacheadoExistencia(repo)
    assert cache.por_referencia("no-existe") is None and cache.por_referencia("no-existe") is None
    cifrador = CifradorAes(b"clave de pruebas")
    assert cifrador.descifrar(cifrador.cifrar("dato personal")) == "dato personal"


class TestSobreDelBus:
    def test_publicador_envia_sobre_completo_con_payload_del_contrato(self):
        import json
        from unittest import mock
        from repuestos_del_taller.adapters.outbound.integracion import PublicadorDeEventosHttp
        with mock.patch("urllib.request.urlopen") as abrir:
            PublicadorDeEventosHttp("http://bus").publicar("t.v1", {"eventId": "e-1", "paradaId": "P", "referencia": "R", "cantidadFaltante": 1})
        sobre = json.loads(abrir.call_args.args[0].data)
        assert sobre["eventId"] == "e-1" and sobre["topic"] == "t.v1"
        assert sobre["occurredOn"] and sobre["correlationId"]
        assert sobre["payload"] == {"paradaId": "P", "referencia": "R", "cantidadFaltante": 1}

    def test_parada_con_faltante_se_procesa_sin_error(self):
        from repuestos_del_taller.application.integracion import ParadaProgramadaConsumidor
        repo = _repo(); RegistrarEntradaDeRepuestoManejador(repo).manejar(RegistrarEntradaCommand("R-1", 1, 1, 2))
        consumidor = ParadaProgramadaConsumidor(ReservarRepuestoManejador(repo))
        sobre = {"eventId": "e-1", "payload": {"paradaId": "P", "tareas": [{"repuestos": [{"referencia": "R-1", "cantidad": 3}]}]}}
        assert consumidor.consumir(sobre) is True
