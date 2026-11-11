"""Humo del dominio «Repuestos del Taller» contra su plataforma de humo.

Solo biblioteca estándar (``urllib``). Recorre, en orden, los eventos que el
servicio consume, los comandos de usuario de su API y la entrega del evento que
publica. Cada paso espera con reintento (máximo 60 s) y falla con código 1 si
algo no ocurrió.

Uso: ``GATEWAY_URL=http://localhost:8080 python smoke/smoke.py``
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = os.environ.get("GATEWAY_URL", "http://localhost:8080").rstrip("/")
ESPERA_MAXIMA = 60.0
TOPICO_FALTANTE = "repuestos-del-taller.faltante-detectado.v1"


class Fallo(RuntimeError):
    """Un paso del escenario no se cumplió dentro del plazo."""


def require(condicion, mensaje: str) -> None:
    if not condicion:
        raise Fallo(mensaje)


def _peticion(metodo: str, ruta: str, payload=None):
    """Devuelve ``(status, cuerpo)``; los 4xx/5xx se devuelven, no se levantan."""
    datos = None if payload is None else json.dumps(payload).encode()
    peticion = urllib.request.Request(BASE + ruta, data=datos, method=metodo,
                                      headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(peticion, timeout=10) as respuesta:
            return respuesta.status, json.loads(respuesta.read() or b"{}")
    except urllib.error.HTTPError as error:
        texto = error.read().decode() or "{}"
        try:
            return error.code, json.loads(texto)
        except ValueError:
            return error.code, {"error": texto}


def esperar(descripcion: str, ruta: str, cumple=lambda cuerpo: True):
    """Reintenta un GET hasta que su cuerpo cumpla la condición."""
    limite = time.monotonic() + ESPERA_MAXIMA
    ultimo = "sin respuesta"
    while time.monotonic() < limite:
        try:
            estado, cuerpo = _peticion("GET", ruta)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            ultimo = error
        else:
            if estado < 400 and cumple(cuerpo):
                return cuerpo
            ultimo = f"HTTP {estado} {cuerpo}"
        time.sleep(0.5)
    raise Fallo(f"{descripcion}: {ultimo}")


def comando(descripcion: str, ruta: str, payload=None, cumple=lambda cuerpo: True):
    """Ejecuta un POST una sola vez por intento: reintenta solo si no hubo respuesta HTTP."""
    limite = time.monotonic() + ESPERA_MAXIMA
    ultimo = "sin respuesta"
    while time.monotonic() < limite:
        try:
            estado, cuerpo = _peticion("POST", ruta, payload)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            ultimo = error
            time.sleep(0.5)
            continue
        if estado < 400 and cumple(cuerpo):
            return cuerpo
        raise Fallo(f"{descripcion}: HTTP {estado} {cuerpo}")
    raise Fallo(f"{descripcion}: {ultimo}")


def emitir(contexto: str, evento: str, payload: dict) -> None:
    """Dispara un evento por el simulador; si no hay simulador, publica en el bus."""
    ruta = f"/sim/simulate/{contexto}/{evento}"
    estado, cuerpo = _peticion("POST", ruta, payload)
    if estado == 202:
        return
    if estado != 404:
        raise Fallo(f"{ruta} respondió {estado}: {cuerpo}")
    sobre = {"eventId": str(uuid.uuid4()), "topic": f"{contexto}.{evento}.v1",
             "occurredOn": "2026-11-20T08:00:00Z",
             "correlationId": str(uuid.uuid4()), "payload": payload}
    comando("publicar en el bus", "/bus/publish", sobre,
            cumple=lambda valor: valor.get("accepted") is True)


def suscriptores(topico: str) -> list[str]:
    config = esperar(f"tópicos del bus ({topico})", "/bus/topics")
    for entrada in config.get("topics", []):
        if entrada.get("topic") == topico:
            return [suscriptor["url"] for suscriptor in entrada.get("subscribers", [])]
    return []


def _faltante_de(recibidos, referencia: str):
    for item in recibidos:
        if item.get("topic") != TOPICO_FALTANTE:
            continue
        if item.get("envelope", {}).get("payload", {}).get("referencia") == referencia:
            return item
    return None


def _entrega_confirmada(eventos):
    for evento in eventos:
        entregas = evento.get("delivered") or {}
        if evento.get("topic") == TOPICO_FALTANTE and entregas and all(entregas.values()):
            return evento
    return None


def verificar_faltante(referencia: str, cantidad: int, parada_id: str) -> str:
    """Quien recibe Faltante detectado depende de la plataforma: en la aislada es el
    simulador (``/sim/received``); en la ensamblada es el dominio real (log del bus)."""
    urls = suscriptores(TOPICO_FALTANTE)
    require(urls, f"nadie está suscripto a {TOPICO_FALTANTE}")
    if any("simulator" in url for url in urls):
        recibidos = esperar("entrega de Faltante detectado a los simuladores", "/sim/received",
                            lambda valor: _faltante_de(valor, referencia) is not None)
        sobre = _faltante_de(recibidos, referencia)["envelope"]
        require(sobre.get("topic") == TOPICO_FALTANTE, f"sobre con tópico inesperado: {sobre}")
        require(sobre.get("occurredOn") and sobre.get("correlationId"),
                f"el sobre no cumple el contrato del bus: {sobre}")
        payload = sobre.get("payload", {})
        require(payload.get("paradaId") == parada_id and payload.get("referencia") == referencia
                and payload.get("cantidadFaltante") == cantidad,
                f"payload de Faltante detectado inesperado: {payload}")
        return "simulador"
    eventos = esperar("entrega de Faltante detectado por el bus", "/bus/events",
                      lambda valor: _entrega_confirmada(valor) is not None)
    confirmado = _entrega_confirmada(eventos)
    return f"bus, {len(confirmado.get('subscribers') or [])} suscriptor(es)"


def reservada(existencia: dict) -> int:
    return sum(reserva["cantidad"] for reserva in existencia.get("reservas", []))


def disponible(existencia: dict) -> int:
    """Existencia usable = física − reservada (invariante del agregado)."""
    return existencia["fisica"] - reservada(existencia)


def existencia_de(referencia: str, descripcion: str, cumple):
    return esperar(f"{descripcion} ({referencia})", f"/api/repuestos/existencia/{referencia}", cumple)


def solicitud_de(solicitud_id: str, cumple):
    return esperar("estado de la solicitud", f"/api/repuestos/solicitud-de-reposicion/{solicitud_id}", cumple)


def historial_de_eventos(pasos: list[str], sufijo: str) -> None:
    repuesto = f"HEL-T40-{sufijo}"

    comando("registrar entrada de repuesto", "/api/repuestos/existencia",
            {"referencia": repuesto, "cantidad": 5, "stock_minimo": 1, "plazo_dias": 7})
    existencia = existencia_de(repuesto, "existencia registrada", lambda valor: valor.get("fisica") == 5)
    require(disponible(existencia) == 5 and existencia["estado"] == "disponible",
            f"existencia inicial inesperada: {existencia}")
    pasos.append("registrar entrada -> física 5, disponible 5")

    parada = {"paradaId": str(uuid.uuid4()), "dronId": "ADV-03",
              "fechaProgramada": "2026-11-20T08:00:00Z",
              "tareas": [{"tareaId": "T-101", "descripcion": "Cambio de helices",
                          "repuestos": [{"referencia": repuesto, "cantidad": 2}]}]}
    emitir("plan-de-mantenimiento", "parada-programada", parada)
    existencia = existencia_de(repuesto, "reserva de la parada",
                               lambda valor: len(valor.get("reservas", [])) == 1)
    require(reservada(existencia) == 2 and disponible(existencia) == 3
            and existencia["estado"] == "reservado", f"la parada no reservó stock: {existencia}")
    pasos.append("parada programada -> reserva de 2, disponible 3")

    orden = {"ordenId": str(uuid.uuid4()), "paradaId": parada["paradaId"], "dronId": "ADV-03",
             "cerradaEn": "2026-11-20T15:30:00Z", "horasHombre": 3.5,
             "consumos": [{"referencia": repuesto, "cantidad": 2, "numeroSerie": None}]}
    emitir("intervenciones", "orden-de-trabajo-cerrada", orden)
    existencia = existencia_de(repuesto, "consumo de la orden cerrada",
                               lambda valor: valor.get("fisica") == 3 and not valor.get("reservas"))
    require(existencia["estado"] == "consumido" and disponible(existencia) == 3,
            f"la OT no confirmó el consumo: {existencia}")
    pasos.append("orden de trabajo cerrada -> consumo, física 3")

    faltante = dict(parada, tareas=[{"tareaId": "T-102", "descripcion": "Faltante",
                                     "repuestos": [{"referencia": repuesto, "cantidad": 5}]}])
    emitir("plan-de-mantenimiento", "parada-programada", faltante)
    destino = verificar_faltante(repuesto, 2, faltante["paradaId"])
    pasos.append(f"parada sin stock -> Faltante detectado entregado ({destino})")


def comandos_de_usuario(pasos: list[str], sufijo: str) -> None:
    usuario = f"USER-{sufijo}"
    comando("registrar entrada de usuario", "/api/repuestos/existencia",
            {"referencia": usuario, "cantidad": 4, "stock_minimo": 1, "plazo_dias": 3})
    existencia_de(usuario, "existencia de usuario", lambda valor: valor.get("fisica") == 4)

    comando("reservar repuesto", f"/api/repuestos/existencia/{usuario}/reservar-repuesto",
            {"orden_trabajo_id": "OT-RESERVA", "cantidad": 1})
    existencia = existencia_de(usuario, "reserva del usuario", lambda valor: reservada(valor) == 1)
    require(disponible(existencia) == 3 and existencia["estado"] == "reservado",
            f"reserva inesperada: {existencia}")
    pasos.append("reservar repuesto -> reservada 1, disponible 3")

    comando("liberar reserva", f"/api/repuestos/existencia/{usuario}/liberar-reserva",
            {"orden_trabajo_id": "OT-RESERVA"})
    existencia = existencia_de(usuario, "reserva liberada", lambda valor: not valor.get("reservas"))
    require(disponible(existencia) == 4 and existencia["estado"] == "disponible",
            f"liberación inesperada: {existencia}")
    pasos.append("liberar reserva -> disponible 4")

    comando("ajustar existencia por conteo", f"/api/repuestos/existencia/{usuario}/ajustar-existencia-por-conteo",
            {"conteo": 3})
    existencia = existencia_de(usuario, "existencia ajustada", lambda valor: valor.get("fisica") == 3)
    require(disponible(existencia) == 3, f"ajuste inesperado: {existencia}")
    pasos.append("ajustar existencia por conteo -> física 3")

    consumo = f"CONS-{sufijo}"
    comando("registrar entrada del repuesto consumido", "/api/repuestos/existencia",
            {"referencia": consumo, "cantidad": 5, "stock_minimo": 0, "plazo_dias": 2})
    existencia_de(consumo, "existencia a consumir", lambda valor: valor.get("fisica") == 5)
    comando("reservar para la OT de consumo", f"/api/repuestos/existencia/{consumo}/reservar-repuesto",
            {"orden_trabajo_id": "OT-CONSUMO", "cantidad": 2})
    existencia_de(consumo, "reserva para consumo", lambda valor: reservada(valor) == 2)
    comando("confirmar consumo", f"/api/repuestos/existencia/{consumo}/confirmar-consumo",
            {"orden_trabajo_id": "OT-CONSUMO"})
    existencia = existencia_de(consumo, "consumo confirmado",
                               lambda valor: valor.get("fisica") == 3 and not valor.get("reservas"))
    require(existencia["estado"] == "consumido", f"consumo inesperado: {existencia}")
    pasos.append("confirmar consumo -> física 3, consumido")

    solicitud_id = str(uuid.uuid4())
    comando("solicitar reposición", "/api/repuestos/solicitud-de-reposicion",
            {"referencia": usuario, "cantidad": 2, "monto": 100, "solicitud_id": solicitud_id})
    solicitud_de(solicitud_id, lambda valor: valor.get("estado") == "abierta")
    comando("aprobar solicitud", f"/api/repuestos/solicitud-de-reposicion/{solicitud_id}/aprobar-solicitud")
    solicitud_de(solicitud_id, lambda valor: valor.get("estado") == "aprobada")
    pasos.append("solicitar reposición -> aprobada")

    cancelar_id = str(uuid.uuid4())
    comando("solicitar reposición a cancelar", "/api/repuestos/solicitud-de-reposicion",
            {"referencia": f"CANCEL-{sufijo}", "cantidad": 1, "monto": 10, "solicitud_id": cancelar_id})
    solicitud_de(cancelar_id, lambda valor: valor.get("estado") == "abierta")
    comando("cancelar solicitud", f"/api/repuestos/solicitud-de-reposicion/{cancelar_id}/cancelar-solicitud")
    solicitud_de(cancelar_id, lambda valor: valor.get("estado") == "cancelada")
    pasos.append("solicitar reposición -> cancelada")


def main() -> int:
    pasos: list[str] = []
    esperar("salud del servicio", "/api/repuestos/health", lambda valor: valor.get("status") == "ok")
    pasos.append("salud del servicio")

    sufijo = uuid.uuid4().hex[:8]
    historial_de_eventos(pasos, sufijo)
    comandos_de_usuario(pasos, sufijo)

    print("Smoke Repuestos del Taller: OK")
    for paso in pasos:
        print(f"- {paso}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Fallo as error:
        print(f"Smoke Repuestos del Taller: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
