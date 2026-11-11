"""Regresiones de la revisión independiente (S50)."""
import asyncio
import json


from repuestos_del_taller.adapters.inbound.http.composicion import RepuestosDelTallerComposicion
from repuestos_del_taller.adapters.outbound.persistencia import (
    RepositorioExistencia, RepositorioSolicitudDeReposicion,
)
from repuestos_del_taller.application.comandos import (
    AprobarSolicitudComando, ConfirmarConsumoComando, RegistrarEntradaDeRepuestoComando,
    ReservarRepuestoComando,
)
from repuestos_del_taller.application.integracion import StockMinimoAlcanzadoObservador
from repuestos_del_taller.application.manejadores import (
    AprobarSolicitudManejador, ConfirmarConsumoManejador, RegistrarEntradaDeRepuestoManejador,
    ReservarRepuestoManejador, SolicitarReposicionManejador,
)


class Cliente:
    """Cliente ASGI mínimo: evita depender de httpx en el entorno hermético."""

    def __init__(self, app): self.app = app

    def post(self, ruta, json_body):
        return asyncio.run(self._llamar(ruta, json_body))

    async def _llamar(self, ruta, cuerpo):
        datos = json.dumps(cuerpo).encode(); respuesta = {}
        async def recibir(): return {"type": "http.request", "body": datos, "more_body": False}
        async def enviar(mensaje):
            if mensaje["type"] == "http.response.start": respuesta["status"] = mensaje["status"]
        await self.app({"type": "http", "method": "POST", "path": ruta, "raw_path": ruta.encode(), "query_string": b"",
                        "headers": [(b"content-type", b"application/json")], "scheme": "http", "server": ("t", 80),
                        "client": ("t", 1), "http_version": "1.1", "root_path": ""}, recibir, enviar)
        return respuesta["status"]


def _preparar():
    existencias = RepositorioExistencia(); solicitudes = RepositorioSolicitudDeReposicion()
    RegistrarEntradaDeRepuestoManejador(existencias).manejar(RegistrarEntradaDeRepuestoComando("R-1", 4, 2, 3))
    ReservarRepuestoManejador(existencias).manejar(ReservarRepuestoComando("R-1", "OT-1", 3))
    observador = StockMinimoAlcanzadoObservador(SolicitarReposicionManejador(solicitudes))
    return existencias, solicitudes, observador


def test_stock_minimo_alcanzado_dispara_solicitar_reposicion() -> None:
    existencias, solicitudes, observador = _preparar()
    ConfirmarConsumoManejador(existencias, observador).manejar(ConfirmarConsumoComando("R-1", "OT-1"))
    assert solicitudes.abierta_de_referencia("R-1") is not None


def test_aprobar_la_solicitud_pone_la_existencia_en_reponiendo() -> None:
    existencias, solicitudes, observador = _preparar()
    ConfirmarConsumoManejador(existencias, observador).manejar(ConfirmarConsumoComando("R-1", "OT-1"))
    abierta = solicitudes.abierta_de_referencia("R-1")
    AprobarSolicitudManejador(solicitudes, existencias).manejar(AprobarSolicitudComando(str(abierta.id)))
    assert existencias.por_referencia("R-1").estado == "reponiendo"


def test_cuerpo_invalido_responde_422_y_no_500() -> None:
    cliente = Cliente(RepuestosDelTallerComposicion().crear_app())
    assert cliente.post("/api/existencia", {"referencia": "R-1"}) == 422
    assert cliente.post("/api/solicitud-de-reposicion", {"referencia": "R-1", "cantidad": 1, "monto": 1, "solicitud_id": "no-uuid"}) == 422


def test_reservar_por_http_publica_el_faltante() -> None:
    publicados = []
    class Falso:
        def publicar(self, topico, evento): publicados.append(topico)
    cliente = Cliente(RepuestosDelTallerComposicion(publicador=Falso()).crear_app())
    cliente.post("/api/existencia", {"referencia": "R-1", "cantidad": 1, "stock_minimo": 0, "plazo_dias": 1})
    assert cliente.post("/api/existencia/R-1/reservar-repuesto", {"orden_trabajo_id": "OT-9", "cantidad": 5}) == 409
    assert publicados == ["repuestos-del-taller.faltante-detectado.v1"]
