"""Smoke end-to-end del dominio usando solo urllib y la plataforma ensamblada."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid


BASE = os.environ.get("GATEWAY_URL", "http://localhost:8080").rstrip("/")


def call(method: str, path: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(BASE + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status, json.loads(response.read() or b"{}")


def eventually(method: str, path: str, payload=None, check=lambda _: True, seconds=60):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        try:
            last = call(method, path, payload)
            if check(last[1]):
                return last[1]
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
            last = error
        time.sleep(0.5)
    raise RuntimeError(f"Timeout esperando {method} {path}: {last}")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def respuesta(method: str, path: str, payload=None):
    """Como call, pero devuelve (status, cuerpo) también en respuestas 4xx/5xx."""
    try:
        return call(method, path, payload)
    except urllib.error.HTTPError as error:
        texto = error.read().decode() or "{}"
        try:
            return error.code, json.loads(texto)
        except ValueError:
            return error.code, {"error": texto}


def emitir(contexto, evento, payload):
    ruta = f"/sim/simulate/{contexto}/{evento}"
    status, response = respuesta("POST", ruta, payload)
    if status == 202:
        return response
    if status != 404:
        raise RuntimeError(f"{ruta} respondió {status}: {response}")
    envelope = {"eventId": str(uuid.uuid4()),
                "topic": f"{contexto}.{evento}.v1",
                "occurredOn": "2026-11-20T08:00:00Z",
                "correlationId": str(uuid.uuid4()), "payload": payload}
    return eventually("POST", "/bus/publish", envelope,
                      check=lambda value: value.get("accepted") is True)


def reservada(existencia) -> int:
    return sum(reserva["cantidad"] for reserva in existencia.get("reservas", []))


def main() -> int:
    steps = []
    eventually("GET", "/api/repuestos/health", check=lambda value: value.get("status") == "ok")
    steps.append("health")

    reference = "HEL-T40"
    eventually("POST", "/api/repuestos/existencia", {
        "referencia": reference, "cantidad": 5, "stock_minimo": 1, "plazo_dias": 7,
    })
    steps.append("registrar entrada")

    parada = {
        "paradaId": "11111111-1111-4111-8111-111111111111", "dronId": "ADV-03",
        "fechaProgramada": "2026-11-20T08:00:00Z", "tareas": [{
            "tareaId": "T-101", "descripcion": "Cambio de helices",
            "repuestos": [{"referencia": reference, "cantidad": 2}],
        }],
    }
    emitir("plan-de-mantenimiento", "parada-programada", parada)
    existencia = eventually("GET", f"/api/repuestos/existencia/{reference}",
                            check=lambda value: len(value.get("reservas", [])) == 1)
    require(reservada(existencia) == 2 and existencia["fisica"] == 5, "la parada no reservó stock")
    steps.append("parada programada -> reserva")

    orden = {
        "ordenId": "22222222-2222-4222-8222-222222222222", "paradaId": parada["paradaId"],
        "dronId": "ADV-03", "cerradaEn": "2026-11-20T15:30:00Z", "horasHombre": 3.5,
        "consumos": [{"referencia": reference, "cantidad": 2, "numeroSerie": None}],
    }
    emitir("intervenciones", "orden-de-trabajo-cerrada", orden)
    existencia = eventually("GET", f"/api/repuestos/existencia/{reference}",
                            check=lambda value: value.get("fisica") == 3 and not value.get("reservas"))
    require(reservada(existencia) == 0, "la OT no confirmó el consumo")
    steps.append("orden cerrada -> consumo")

    faltante = dict(parada, tareas=[{"tareaId": "T-102", "descripcion": "Faltante",
                                     "repuestos": [{"referencia": reference, "cantidad": 5}]}])
    emitir("plan-de-mantenimiento", "parada-programada", faltante)
    received = eventually("GET", "/sim/received",
                          check=lambda value: any(item.get("topic") == "repuestos-del-taller.faltante-detectado.v1"
                                                   for item in value))
    payload = next(item for item in received
                   if item["topic"] == "repuestos-del-taller.faltante-detectado.v1")["envelope"]["payload"]
    require(payload["referencia"] == reference and payload["cantidadFaltante"] == 2,
            f"payload de Faltante detectado inesperado: {payload}")
    steps.append("faltante detectado -> suscriptor")

    user_ref = "USER-REF"
    eventually("POST", "/api/repuestos/existencia", {
        "referencia": user_ref, "cantidad": 4, "stock_minimo": 1, "plazo_dias": 3,
    })
    eventually("POST", f"/api/repuestos/existencia/{user_ref}/reservar-repuesto",
               {"orden_trabajo_id": "USER-OT", "cantidad": 1})
    eventually("POST", f"/api/repuestos/existencia/{user_ref}/liberar-reserva",
               {"orden_trabajo_id": "USER-OT"})
    eventually("POST", f"/api/repuestos/existencia/{user_ref}/ajustar-existencia-por-conteo", {"conteo": 4})
    solicitud_id = str(uuid.uuid4())
    eventually("POST", "/api/repuestos/solicitud-de-reposicion", {
        "referencia": user_ref, "cantidad": 2, "monto": 100, "solicitud_id": solicitud_id,
    })
    eventually("POST", f"/api/repuestos/solicitud-de-reposicion/{solicitud_id}/aprobar-solicitud")
    solicitud = eventually("GET", f"/api/repuestos/solicitud-de-reposicion/{solicitud_id}",
                           check=lambda value: value.get("estado") == "aprobada")
    require(solicitud["estado"] == "aprobada", "no se aprobó la solicitud")
    cancel_id = str(uuid.uuid4())
    eventually("POST", "/api/repuestos/solicitud-de-reposicion", {
        "referencia": "CANCEL-REF", "cantidad": 1, "monto": 10, "solicitud_id": cancel_id,
    })
    eventually("POST", f"/api/repuestos/solicitud-de-reposicion/{cancel_id}/cancelar-solicitud")
    steps.append("comandos principales de usuario")

    print("Smoke Repuestos del Taller: OK")
    for step in steps:
        print(f"- {step}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Smoke Repuestos del Taller: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
