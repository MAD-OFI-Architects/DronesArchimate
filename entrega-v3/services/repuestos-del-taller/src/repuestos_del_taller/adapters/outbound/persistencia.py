"""Repositorios de infraestructura.

La implementación mantiene un almacén en memoria para las pruebas herméticas y
acepta una conexión DB-API opcional para que el composition root pueda conectar
PostgreSQL sin filtrar ese detalle al dominio.
"""
from __future__ import annotations

import threading
import time
from typing import Any
import uuid

from ...domain.existencias.existencia import Existencia
from ...domain.existencias.repositorio import IExistenciaRepository
from ...domain.reposicion.repositorio import ISolicitudDeReposicionRepository
from ...domain.reposicion.solicitud_de_reposicion import SolicitudDeReposicion


class RepositorioExistencia(IExistenciaRepository):
    def __init__(self, conexion: Any | None = None) -> None:
        self.conexion = conexion
        self._datos: dict[str, Existencia] = {}
        self._lock = threading.RLock()

    def por_referencia(self, referencia: str) -> Existencia | None:
        with self._lock:
            return self._datos.get(referencia)

    def guardar(self, existencia: Existencia) -> None:
        with self._lock:
            self._datos[existencia.referencia] = existencia


class RepositorioCacheadoExistencia(IExistenciaRepository):
    def __init__(self, repositorio: IExistenciaRepository, ttl: float = 60.0) -> None:
        self.repositorio = repositorio
        self.ttl = ttl
        self._cache: dict[str, tuple[float, Existencia | None]] = {}
        self._lock = threading.RLock()

    def por_referencia(self, referencia: str) -> Existencia | None:
        ahora = time.monotonic()
        with self._lock:
            entrada = self._cache.get(referencia)
            if entrada and ahora - entrada[0] < self.ttl:
                return entrada[1]
        valor = self.repositorio.por_referencia(referencia)
        with self._lock:
            self._cache[referencia] = (ahora, valor)
        return valor

    def guardar(self, existencia: Existencia) -> None:
        self.repositorio.guardar(existencia)
        with self._lock:
            self._cache.pop(existencia.referencia, None)


class RepositorioSolicitudDeReposicion(ISolicitudDeReposicionRepository):
    def __init__(self, conexion: Any | None = None) -> None:
        self.conexion = conexion
        self._datos: dict[uuid.UUID, SolicitudDeReposicion] = {}
        self._lock = threading.RLock()

    def por_id(self, id_: uuid.UUID) -> SolicitudDeReposicion | None:
        with self._lock:
            return self._datos.get(id_)

    def abierta_de_referencia(self, referencia: str) -> SolicitudDeReposicion | None:
        with self._lock:
            return next((s for s in self._datos.values() if s.referencia == referencia and s.estado == "abierta"), None)

    def guardar(self, solicitud: SolicitudDeReposicion) -> None:
        with self._lock:
            self._datos[solicitud.id] = solicitud


class RepositorioCacheadoSolicitudDeReposicion(ISolicitudDeReposicionRepository):
    def __init__(self, repositorio: ISolicitudDeReposicionRepository, ttl: float = 60.0) -> None:
        self.repositorio = repositorio
        self.ttl = ttl
        self._cache: dict[uuid.UUID, tuple[float, SolicitudDeReposicion | None]] = {}

    def por_id(self, id_: uuid.UUID) -> SolicitudDeReposicion | None:
        ahora = time.monotonic()
        entrada = self._cache.get(id_)
        if entrada and ahora - entrada[0] < self.ttl:
            return entrada[1]
        valor = self.repositorio.por_id(id_)
        self._cache[id_] = (ahora, valor)
        return valor

    def abierta_de_referencia(self, referencia: str) -> SolicitudDeReposicion | None:
        return self.repositorio.abierta_de_referencia(referencia)

    def guardar(self, solicitud: SolicitudDeReposicion) -> None:
        self.repositorio.guardar(solicitud)
        self._cache.pop(solicitud.id, None)
