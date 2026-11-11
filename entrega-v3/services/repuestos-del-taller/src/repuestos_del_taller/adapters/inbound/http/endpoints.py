"""Endpoints HTTP y serialización de Problem Details."""
from __future__ import annotations

import uuid
from dataclasses import asdict, is_dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ....application.comandos import *
from ....domain.compartido.errores import ErrorDeDominio, ViolacionDeReglaDeNegocio


def _datos(obj: Any) -> dict:
    if is_dataclass(obj): return asdict(obj)
    if hasattr(obj, "crear_memento"): return asdict(obj.crear_memento())
    return {"valor": str(obj)}


class RepuestosDelTallerEndpoints:
    rutas = (
        "/api/existencia", "reservar-repuesto", "liberar-reserva", "confirmar-consumo",
        "ajustar-existencia-por-conteo", "/api/solicitud-de-reposicion", "aprobar-solicitud", "cancelar-solicitud",
    )

    def __init__(self, registrar, reservar, liberar, consumir, ajustar, solicitar, aprobar, cancelar, existencias, solicitudes, procesador, consumidores) -> None:
        self.manejadores = {"registrar": registrar, "reservar": reservar, "liberar": liberar, "consumir": consumir, "ajustar": ajustar, "solicitar": solicitar, "aprobar": aprobar, "cancelar": cancelar}
        self.existencias = existencias; self.solicitudes = solicitudes
        self.procesador = procesador; self.consumidores = consumidores

    def _ejecutar(self, nombre: str, comando):
        return _datos(self.manejadores[nombre].manejar(comando))

    def health(self) -> dict: return {"status": "ok"}

    def _entrada(self, topic: str, envelope: dict) -> dict:
        consumidor = self.consumidores[topic]
        self.procesador.procesar(envelope, consumidor.consumir)
        return {"procesado": True}

    def crear_app(self):
        app = FastAPI(title="Repuestos del Taller")
        app.get("/health")(self.health)
        app.get("/api/health")(self.health)
        async def body(request: Request) -> dict:
            return await request.json()

        async def ejecutar(nombre, construir):
            try:
                return self._ejecutar(nombre, construir())
            except (ErrorDeDominio, ViolacionDeReglaDeNegocio) as error:
                return JSONResponse(status_code=409, content={"error": str(error)})
            except LookupError as error:
                return JSONResponse(status_code=404, content={"error": str(error)})
            except (ValueError, TypeError) as error:
                return JSONResponse(status_code=422, content={"error": str(error)})

        @app.post("/api/existencia")
        async def registrar(request: Request):
            cuerpo = await body(request)
            return await ejecutar("registrar", lambda: RegistrarEntradaDeRepuestoComando(**cuerpo))

        @app.post("/api/existencia/{referencia}/reservar-repuesto")
        async def reservar(referencia: str, request: Request):
            cuerpo = await body(request)
            return await ejecutar("reservar", lambda: ReservarRepuestoComando(referencia=referencia, **cuerpo))

        @app.post("/api/existencia/{referencia}/liberar-reserva")
        async def liberar(referencia: str, request: Request):
            cuerpo = await body(request)
            return await ejecutar("liberar", lambda: LiberarReservaComando(referencia=referencia, **cuerpo))

        @app.post("/api/existencia/{referencia}/confirmar-consumo")
        async def consumir(referencia: str, request: Request):
            cuerpo = await body(request)
            return await ejecutar("consumir", lambda: ConfirmarConsumoComando(referencia=referencia, **cuerpo))

        @app.post("/api/existencia/{referencia}/ajustar-existencia-por-conteo")
        async def ajustar(referencia: str, request: Request):
            cuerpo = await body(request)
            return await ejecutar("ajustar", lambda: AjustarExistenciaPorConteoComando(referencia=referencia, **cuerpo))

        @app.get("/api/existencia/{referencia}")
        async def obtener_existencia(referencia: str):
            existencia = self.existencias.por_referencia(referencia)
            return _datos(existencia) if existencia else JSONResponse(status_code=404, content={"error": "REFERENCIA_INEXISTENTE"})

        @app.post("/api/solicitud-de-reposicion")
        async def solicitar(request: Request):
            cuerpo = await body(request)
            return await ejecutar("solicitar", lambda: SolicitarReposicionComando(**cuerpo))

        @app.post("/api/solicitud-de-reposicion/{solicitud_id}/aprobar-solicitud")
        async def aprobar(solicitud_id: str):
            return await ejecutar("aprobar", lambda: AprobarSolicitudComando(solicitud_id=solicitud_id))

        @app.post("/api/solicitud-de-reposicion/{solicitud_id}/cancelar-solicitud")
        async def cancelar(solicitud_id: str):
            return await ejecutar("cancelar", lambda: CancelarSolicitudComando(solicitud_id=solicitud_id))

        @app.get("/api/solicitud-de-reposicion/{solicitud_id}")
        async def obtener_solicitud(solicitud_id: str):
            try:
                solicitud = self.solicitudes.por_id(uuid.UUID(solicitud_id))
            except ValueError:
                solicitud = None
            return _datos(solicitud) if solicitud else JSONResponse(status_code=404, content={"error": "SOLICITUD_INEXISTENTE"})

        @app.post("/events/{topic}")
        async def recibir_evento(topic: str, request: Request):
            envelope = await body(request)
            if topic not in self.consumidores:
                return JSONResponse(status_code=404, content={"error": "TOPICO_NO_CONSUMIDO"})
            return self._entrada(topic, envelope)
        return app
