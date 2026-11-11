"""Endpoints HTTP y serialización de Problem Details."""
from __future__ import annotations

import re
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


def _codigo(nombre_de_regla: str) -> str:
    """ExistenciaInsuficiente → EXISTENCIA_INSUFICIENTE (código del contrato)."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", nombre_de_regla).upper()


def _problema(estado: int, titulo: str, detalle: str, **extensiones: str) -> JSONResponse:
    """Problem Details (RFC 9457), igual que Intervenciones; ``error`` se conserva por compatibilidad."""
    cuerpo = {"type": "about:blank", "title": titulo, "status": estado, "detail": detalle, "error": detalle, **extensiones}
    return JSONResponse(status_code=estado, content=cuerpo, media_type="application/problem+json")


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
            except ViolacionDeReglaDeNegocio as error:
                regla = type(error.regla).__name__
                return _problema(422, "Regla de negocio incumplida", str(error), regla=regla, codigo=_codigo(regla))
            except ErrorDeDominio as error:
                return _problema(400, "Dato inválido para el dominio", str(error))
            except LookupError as error:
                return _problema(404, "Recurso no encontrado", str(error), codigo=str(error))
            except (ValueError, TypeError) as error:
                return _problema(400, "Solicitud inválida", str(error))

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
            return _datos(existencia) if existencia else _problema(404, "Recurso no encontrado", "REFERENCIA_INEXISTENTE", codigo="REFERENCIA_INEXISTENTE")

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
            return _datos(solicitud) if solicitud else _problema(404, "Recurso no encontrado", "SOLICITUD_INEXISTENTE", codigo="SOLICITUD_INEXISTENTE")

        @app.post("/events/{topic}")
        async def recibir_evento(topic: str, request: Request):
            envelope = await body(request)
            if topic not in self.consumidores:
                return _problema(404, "Recurso no encontrado", "TOPICO_NO_CONSUMIDO", codigo="TOPICO_NO_CONSUMIDO")
            return self._entrada(topic, envelope)
        return app
