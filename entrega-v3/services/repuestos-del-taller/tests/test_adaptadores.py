"""Pruebas herméticas de cada comando y de patrones de infraestructura."""
import uuid

from repuestos_del_taller.adapters.outbound.persistencia import RepositorioCacheadoExistencia, RepositorioExistencia
from repuestos_del_taller.adapters.outbound.seguridad import CifradorAes
from repuestos_del_taller.application.comandos import (
    RegistrarEntradaDeRepuestoComando as RegistrarEntradaCommand,
    ReservarRepuestoComando as ReservarCommand,
)
from repuestos_del_taller.application.manejadores import (
    RegistrarEntradaDeRepuestoManejador, ReservarRepuestoManejador, SolicitarReposicionManejador,
)


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


class TestBandejaDeSalida:
    def test_despacha_cifrada_y_publica_con_el_mismo_event_id(self):
        from repuestos_del_taller.adapters.outbound.integracion import BandejaDeSalida, PublicadorConBandeja

        class Bus:
            def __init__(self): self.enviados = []
            def publicar(self, topico, evento): self.enviados.append((topico, evento))

        bus = Bus()
        bandeja = BandejaDeSalida(CifradorAes(b"clave de pruebas"))
        bandeja.agregar("t", {"eventId": "e-1", "x": 1})
        assert "e-1" not in bandeja._almacen.pendientes()[0][1]
        assert bandeja.despachar(bus) == 1 and bus.enviados == [("t", {"eventId": "e-1", "x": 1})]
        PublicadorConBandeja(bandeja, bus).publicar("t2", {"eventId": "e-2"})
        assert bus.enviados[-1][0] == "t2"

    def test_marca_fallido_tras_agotar_reintentos_sin_borrar(self):
        from repuestos_del_taller.adapters.outbound.integracion import BandejaDeSalida

        class BusCaido:
            def publicar(self, topico, evento): raise OSError()

        bandeja = BandejaDeSalida(CifradorAes(b"clave de pruebas"))
        bandeja.agregar("t", {"eventId": "e-1"})
        for _ in range(3): bandeja.despachar(BusCaido(), 3)
        assert (bandeja.pendientes, bandeja.fallidos) == (0, 1)


def test_observador_envia_aviso_por_el_puerto_acl():
    from repuestos_del_taller.application.integracion import StockMinimoAlcanzadoObservador
    from repuestos_del_taller.application.puertos import IEnviarAviso
    from repuestos_del_taller.adapters.outbound.persistencia import RepositorioSolicitudDeReposicion
    from repuestos_del_taller.domain.existencias.eventos import StockMinimoAlcanzado
    import dataclasses

    class Aviso(IEnviarAviso):
        def __init__(self): self.llamadas = []
        def enviar(self, d, a, m): self.llamadas.append(d)

    aviso = Aviso()
    obs = StockMinimoAlcanzadoObservador(SolicitarReposicionManejador(RepositorioSolicitudDeReposicion()), aviso=aviso)
    campos = {f.name: "R-1" if f.name == "referencia" else 1 for f in dataclasses.fields(StockMinimoAlcanzado) if f.init}
    obs.observar(StockMinimoAlcanzado(**campos), str(uuid.uuid4()))
    assert aviso.llamadas == ["compras"]
