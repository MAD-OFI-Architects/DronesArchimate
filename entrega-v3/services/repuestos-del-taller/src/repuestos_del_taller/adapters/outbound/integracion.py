"""Bus, ACL, outbox e idempotencia."""
from __future__ import annotations

import json
import os
import threading
import urllib.request
import uuid
from datetime import datetime, timezone
from collections.abc import Callable
from typing import Any

from ...application.puertos import Cifrador, IEnviarAviso, IPublicadorDeEventos
from .persistencia import crear_esquema


class EnviarAvisoAdapter(IEnviarAviso):
    def __init__(self, base_url: str | None = None, timeout: float = 3.0) -> None:
        self.base_url = (base_url or os.getenv("SIMULATORS_URL", "")).rstrip("/")
        self.timeout = timeout

    def enviar(self, destinatario: str, asunto: str, mensaje: str) -> None:
        if not self.base_url:
            return
        payload = json.dumps({"destinatario": destinatario, "asunto": asunto, "mensaje": mensaje}).encode()
        request = urllib.request.Request(self.base_url + "/api/notificaciones/enviar-aviso", payload, {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout):
            pass


class PublicadorDeEventosHttp:
    def __init__(self, bus_url: str | None = None, timeout: float = 3.0) -> None:
        self.bus_url = (bus_url or os.getenv("BUS_URL", "")).rstrip("/")
        self.timeout = timeout

    def publicar(self, topico: str, evento: dict) -> None:
        if not self.bus_url:
            return
        payload = {clave: valor for clave, valor in evento.items() if clave != "eventId"}
        sobre = {
            "eventId": evento.get("eventId", str(uuid.uuid4())), "topic": topico,
            "occurredOn": datetime.now(timezone.utc).isoformat(),
            "correlationId": str(uuid.uuid4()), "payload": payload,
        }
        body = json.dumps(sobre).encode()
        request = urllib.request.Request(self.bus_url + "/publish", body, {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout):
            pass


class AlmacenDeBandejaEnMemoria:
    """Almacén de la bandeja para pruebas herméticas; no sobrevive a un reinicio."""

    def __init__(self) -> None:
        self.filas: dict[str, dict] = {}

    def guardar(self, id_: str, topico: str, carga: str) -> None:
        self.filas.setdefault(id_, dict(topico=topico, carga=carga, intentos=0, estado="pendiente"))

    def pendientes(self) -> list[tuple[str, str, int]]:
        return [(i, f["carga"], f["intentos"]) for i, f in self.filas.items() if f["estado"] == "pendiente"]

    def marcar_enviado(self, id_: str) -> None:
        self.filas[id_]["estado"] = "enviado"

    def registrar_fallo(self, id_: str, intentos: int, agotado: bool) -> None:
        self.filas[id_].update(intentos=intentos, estado="fallido" if agotado else "pendiente")

    def contar(self, estado: str) -> int:
        return sum(1 for f in self.filas.values() if f["estado"] == estado)


class AlmacenDeBandejaSql:
    """Outbox durable en PostgreSQL: el evento queda guardado (cifrado) antes de intentar enviarlo."""

    def __init__(self, conexion: Any) -> None:
        self._conexion = conexion
        self._lock = threading.RLock()
        crear_esquema(conexion)

    def guardar(self, id_: str, topico: str, carga: str) -> None:
        with self._lock:
            self._conexion.execute(
                "INSERT INTO bandeja_de_salida (id, topico, carga) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (id_, topico, carga))

    def pendientes(self) -> list[tuple[str, str, int]]:
        with self._lock:
            filas = self._conexion.execute(
                "SELECT id, carga, intentos FROM bandeja_de_salida WHERE estado = 'pendiente' ORDER BY creado, id").fetchall()
        return [(f[0], f[1], f[2]) for f in filas]

    def marcar_enviado(self, id_: str) -> None:
        with self._lock:
            self._conexion.execute("UPDATE bandeja_de_salida SET estado = 'enviado' WHERE id = %s", (id_,))

    def registrar_fallo(self, id_: str, intentos: int, agotado: bool) -> None:
        with self._lock:
            self._conexion.execute(
                "UPDATE bandeja_de_salida SET intentos = %s, estado = %s WHERE id = %s",
                (intentos, "fallido" if agotado else "pendiente", id_))

    def contar(self, estado: str) -> int:
        with self._lock:
            return self._conexion.execute("SELECT count(*) FROM bandeja_de_salida WHERE estado = %s", (estado,)).fetchone()[0]


class BandejaDeSalida:
    """Outbox: el evento se guarda cifrado y luego se despacha; si el bus falla se reintenta y,
    agotados los intentos, queda marcado como fallido (nunca se borra)."""

    def __init__(self, cifrador: Cifrador, almacen: Any = None) -> None:
        self._cifrador = cifrador
        self._almacen = almacen if almacen is not None else AlmacenDeBandejaEnMemoria()
        self._despacho = threading.Lock()

    def agregar(self, topico: str, payload: dict) -> None:
        event_id = str(payload.get("eventId") or uuid.uuid4())
        item = {"eventId": event_id, "topic": topico, "payload": payload}
        self._almacen.guardar(event_id, topico, self._cifrador.cifrar(json.dumps(item)))

    def despachar(self, publicador: PublicadorDeEventosHttp, max_reintentos: int = 3) -> int:
        enviados = 0
        with self._despacho:
            for id_, cifrado, intentos in self._almacen.pendientes():
                item = json.loads(self._cifrador.descifrar(cifrado))
                try:
                    publicador.publicar(item["topic"], item["payload"])
                except Exception:
                    self._almacen.registrar_fallo(id_, intentos + 1, intentos + 1 >= max_reintentos)
                else:
                    self._almacen.marcar_enviado(id_); enviados += 1
        return enviados

    @property
    def pendientes(self) -> int:
        return self._almacen.contar("pendiente")

    @property
    def fallidos(self) -> int:
        return self._almacen.contar("fallido")


class PublicadorConBandeja(IPublicadorDeEventos):
    """Publica por outbox: registra el evento en la bandeja y la despacha."""
    def __init__(self, bandeja: BandejaDeSalida, publicador: PublicadorDeEventosHttp) -> None:
        self._bandeja = bandeja
        self._publicador = publicador

    def publicar(self, topico: str, evento: dict) -> None:
        self._bandeja.agregar(topico, evento)
        self._bandeja.despachar(self._publicador)


class RegistroDeProcesadosEnMemoria:
    def __init__(self) -> None:
        self._ids: set[str] = set()

    def contiene(self, event_id: str) -> bool:
        return event_id in self._ids

    def marcar(self, event_id: str) -> None:
        self._ids.add(event_id)


class RegistroDeProcesadosSql:
    """Inbox durable: los eventos ya procesados sobreviven a un reinicio del servicio."""

    def __init__(self, conexion: Any) -> None:
        self._conexion = conexion
        self._lock = threading.RLock()
        crear_esquema(conexion)

    def contiene(self, event_id: str) -> bool:
        with self._lock:
            return self._conexion.execute("SELECT 1 FROM bandeja_de_entrada WHERE event_id = %s", (event_id,)).fetchone() is not None

    def marcar(self, event_id: str) -> None:
        with self._lock:
            self._conexion.execute("INSERT INTO bandeja_de_entrada (event_id) VALUES (%s) ON CONFLICT (event_id) DO NOTHING", (event_id,))


class ProcesadorDeMensajeEntrante:
    """Inbox: un evento se marca como procesado solo cuando su consumidor terminó; si falla, se reintenta
    (los consumidores son idempotentes por elemento)."""

    def __init__(self, registro: Any = None) -> None:
        self._registro = registro if registro is not None else RegistroDeProcesadosEnMemoria()
        self._lock = threading.Lock()

    def procesar(self, evento: dict, consumidor: Callable[[dict], object]) -> bool:
        event_id = str(evento.get("eventId", ""))
        with self._lock:
            if not event_id or self._registro.contiene(event_id):
                return False
            consumidor(evento)
            self._registro.marcar(event_id)
            return True
