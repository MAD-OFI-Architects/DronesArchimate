"""Repositorios de infraestructura.

``RepositorioExistenciaSql`` y ``RepositorioSolicitudDeReposicionSql`` persisten
el memento de cada agregado en PostgreSQL (``DATABASE_URL``); los repositorios en
memoria quedan como alternativa explícita para pruebas herméticas.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from typing import Any
import uuid

from ...domain.existencias.existencia import Existencia
from ...domain.existencias.memento import ExistenciaMemento, ReservaDeRepuestoMemento
from ...domain.existencias.repositorio import IExistenciaRepository
from ...domain.reposicion.repositorio import ISolicitudDeReposicionRepository
from ...domain.reposicion.memento import SolicitudDeReposicionMemento
from ...domain.reposicion.solicitud_de_reposicion import SolicitudDeReposicion

ESQUEMA = (
    "CREATE TABLE IF NOT EXISTS existencia (referencia TEXT PRIMARY KEY, memento TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS solicitud_de_reposicion ("
    "id TEXT PRIMARY KEY, referencia TEXT NOT NULL, estado TEXT NOT NULL, memento TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS bandeja_de_salida (id TEXT PRIMARY KEY, topico TEXT NOT NULL, carga TEXT NOT NULL, "
    "intentos INTEGER NOT NULL DEFAULT 0, estado TEXT NOT NULL DEFAULT 'pendiente', creado TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS bandeja_de_entrada (event_id TEXT PRIMARY KEY, procesado TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)",
)


def crear_esquema(conexion: Any) -> None:
    for sentencia in ESQUEMA:
        conexion.execute(sentencia)


class RepositorioExistencia(IExistenciaRepository):
    def __init__(self) -> None:
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
    def __init__(self) -> None:
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


class RepositorioExistenciaSql(IExistenciaRepository):
    """Persiste ``ExistenciaMemento`` como JSON; ``conexion`` sigue la interfaz de psycopg (``execute``)."""

    def __init__(self, conexion: Any) -> None:
        self._conexion = conexion
        self._lock = threading.RLock()
        crear_esquema(conexion)

    def por_referencia(self, referencia: str) -> Existencia | None:
        with self._lock:
            fila = self._conexion.execute("SELECT memento FROM existencia WHERE referencia = %s", (referencia,)).fetchone()
        if fila is None:
            return None
        datos = json.loads(fila[0])
        reservas = tuple(ReservaDeRepuestoMemento(**r) for r in datos.pop("reservas"))
        return Existencia.restaurar_desde(ExistenciaMemento(**datos, reservas=reservas))

    def guardar(self, existencia: Existencia) -> None:
        memento = json.dumps(asdict(existencia.crear_memento()))
        with self._lock:
            self._conexion.execute(
                "INSERT INTO existencia (referencia, memento) VALUES (%s, %s) "
                "ON CONFLICT (referencia) DO UPDATE SET memento = EXCLUDED.memento",
                (existencia.referencia, memento),
            )


class RepositorioSolicitudDeReposicionSql(ISolicitudDeReposicionRepository):
    def __init__(self, conexion: Any) -> None:
        self._conexion = conexion
        self._lock = threading.RLock()
        crear_esquema(conexion)

    def _leer(self, condicion: str, valor: str) -> SolicitudDeReposicion | None:
        with self._lock:
            fila = self._conexion.execute(
                f"SELECT memento FROM solicitud_de_reposicion WHERE {condicion} LIMIT 1", (valor,)).fetchone()
        if fila is None:
            return None
        return SolicitudDeReposicion.restaurar_desde(SolicitudDeReposicionMemento(**json.loads(fila[0])))

    def por_id(self, id_: uuid.UUID) -> SolicitudDeReposicion | None:
        return self._leer("id = %s", str(id_))

    def abierta_de_referencia(self, referencia: str) -> SolicitudDeReposicion | None:
        return self._leer("referencia = %s AND estado = 'abierta'", referencia)

    def guardar(self, solicitud: SolicitudDeReposicion) -> None:
        memento = solicitud.crear_memento()
        with self._lock:
            self._conexion.execute(
                "INSERT INTO solicitud_de_reposicion (id, referencia, estado, memento) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET estado = EXCLUDED.estado, memento = EXCLUDED.memento",
                (memento.id, memento.referencia, solicitud.estado, json.dumps(asdict(memento))),
            )
