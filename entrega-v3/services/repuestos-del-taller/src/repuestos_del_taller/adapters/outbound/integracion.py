"""Bus, ACL, outbox e idempotencia."""
from __future__ import annotations

import json
import os
import urllib.request
import uuid
from datetime import datetime, timezone
from collections.abc import Callable

from ...application.puertos import IEnviarAviso


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


class BandejaDeSalida:
    def __init__(self) -> None:
        self._pendientes: list[dict] = []

    def agregar(self, topico: str, payload: dict) -> None:
        self._pendientes.append({"eventId": str(uuid.uuid4()), "topic": topico, "payload": payload, "intentos": 0})

    def despachar(self, publicador: PublicadorDeEventosHttp, max_reintentos: int = 3) -> int:
        enviados = 0
        for item in list(self._pendientes):
            try:
                publicador.publicar(item["topic"], item["payload"])
                self._pendientes.remove(item); enviados += 1
            except Exception:
                item["intentos"] += 1
                if item["intentos"] >= max_reintentos:
                    self._pendientes.remove(item)
        return enviados


class ProcesadorDeMensajeEntrante:
    def __init__(self) -> None:
        self._procesados: set[str] = set()

    def procesar(self, evento: dict, consumidor: Callable[[dict], object]) -> bool:
        event_id = str(evento.get("eventId", ""))
        if not event_id or event_id in self._procesados:
            return False
        consumidor(evento)
        self._procesados.add(event_id)
        return True
