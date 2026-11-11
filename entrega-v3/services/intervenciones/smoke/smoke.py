#!/usr/bin/env python3
"""Humo e2e del dominio Intervenciones: bus + simuladores + servicio real, a través del gateway."""
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8080").rstrip("/")
API = f"{GATEWAY}/api/intervenciones/orden-de-trabajo"
SIM = f"{GATEWAY}/sim"
TOPICO_CERRADA = "intervenciones.orden-de-trabajo-cerrada.v1"
ESPERA_MAXIMA = 60
PASOS = []


def http(metodo, url, cuerpo=None):
    datos = None if cuerpo is None else json.dumps(cuerpo).encode()
    peticion = urllib.request.Request(url, datos, {"Content-Type": "application/json"}, method=metodo)
    try:
        with urllib.request.urlopen(peticion, timeout=10) as r:
            texto = r.read().decode()
            return r.status, json.loads(texto) if texto else None
    except urllib.error.HTTPError as e:
        texto = e.read().decode()
        try:
            return e.code, json.loads(texto) if texto else None
        except ValueError:
            return e.code, texto
    except (urllib.error.URLError, OSError):
        return 0, None


def esperar(descripcion, condicion):
    limite = time.time() + ESPERA_MAXIMA
    ultimo = None
    while time.time() < limite:
        ultimo = condicion()
        if ultimo:
            return ultimo
        time.sleep(1)
    raise AssertionError(f"Tiempo agotado ({ESPERA_MAXIMA} s): {descripcion}")


def paso(descripcion, accion):
    accion()
    PASOS.append(descripcion)
    print(f"  ok  {descripcion}")


def exigir(condicion, mensaje):
    if not condicion:
        raise AssertionError(mensaje)


def orden_de_parada(parada):
    estado, cuerpo = http("GET", f"{API}/por-parada/{parada}")
    return cuerpo if estado == 200 else None


def estado_de(orden_id):
    estado, cuerpo = http("GET", f"{API}/{orden_id}")
    exigir(estado == 200, f"GET orden {orden_id} respondió {estado}")
    return cuerpo


def comando(orden_id, nombre, cuerpo=None):
    estado, respuesta = http("POST", f"{API}/{orden_id}/{nombre}", cuerpo or {})
    exigir(estado == 204, f"{nombre} respondió {estado}: {respuesta}")


def emitir(contexto, evento, payload):
    estado, respuesta = http("POST", f"{SIM}/simulate/{contexto}/{evento}", payload)
    if estado == 404 and contexto == "repuestos-del-taller":
        envelope = {"eventId": str(uuid.uuid4()),
                    "topic": f"{contexto}.{evento}.v1",
                    "occurredOn": "2026-11-20T08:00:00Z",
                    "correlationId": str(uuid.uuid4()), "payload": payload}
        estado, respuesta = http("POST", f"{GATEWAY}/bus/publish", envelope)
    exigir(estado == 202, f"el simulador no publicó {contexto}/{evento}: {estado} {respuesta}")


def verificar_estado(orden_id, esperado):
    actual = estado_de(orden_id)["estado"]
    exigir(actual == esperado, f"estado esperado {esperado}, actual {actual}")


def levantar():
    esperar("simuladores y bus disponibles", lambda: http("GET", f"{SIM}/health")[0] == 200)
    esperar("servicio Intervenciones disponible", lambda: 0 < http("GET", f"{API}/por-parada/{uuid.uuid4()}")[0] < 500)


def parada_programada(parada):
    emitir("plan-de-mantenimiento", "parada-programada", {
        "paradaId": parada, "dronId": "ADV-03", "fechaProgramada": "2026-11-20T08:00:00Z",
        "tareas": [{"tareaId": "T-101", "descripcion": "Cambio de hélices",
                    "repuestos": [{"referencia": "HEL-T40", "cantidad": 2}]}]})
    orden = esperar("la parada programada abre una orden", lambda: orden_de_parada(parada))
    exigir(orden["estado"] == "Abierta" and orden["dronId"] == "ADV-03", f"orden inesperada: {orden}")
    return orden["id"]


def faltante_detectado(parada, orden_id):
    emitir("repuestos-del-taller", "faltante-detectado", {"paradaId": parada, "referencia": "HEL-T40", "cantidadFaltante": 1})
    esperar("el faltante pone la orden en espera", lambda: estado_de(orden_id)["estado"] == "EnEspera")
    exigir("HEL-T40" in (estado_de(orden_id)["motivoDeEspera"] or ""), "el motivo de espera no cita el repuesto")


def ciclo_de_vida(orden_id):
    comando(orden_id, "asignar-tecnico", {"tecnico": "Ana"})
    exigir(estado_de(orden_id)["tecnico"] == "Ana", "el técnico no quedó asignado")
    comando(orden_id, "registrar-ejecucion-de-tarea", {
        "tareaId": str(uuid.uuid4()), "descripcion": "Cambio de hélices", "resultado": "Realizada",
        "ejecutadaPor": "Ana", "horas": 3.5})
    verificar_estado(orden_id, "EnEjecucion")
    comando(orden_id, "registrar-consumo-de-repuesto", {
        "consumoId": str(uuid.uuid4()), "referencia": "HEL-T40", "cantidad": 2, "requiereSerie": False})
    comando(orden_id, "registrar-hallazgo", {"descripcion": "Desgaste leve en el soporte"})
    comando(orden_id, "registrar-vuelo-de-prueba", {
        "realizadoEn": "2026-11-20T14:00:00Z", "duracionEnMinutos": 8, "aprobado": True, "observaciones": "Sin novedades"})
    verificar_estado(orden_id, "Ejecutada")
    comando(orden_id, "liberar-dron", {"liberacionId": str(uuid.uuid4()), "liberadaPor": "Beto"})
    verificar_estado(orden_id, "Liberada")
    comando(orden_id, "cerrar-orden-de-trabajo")
    orden = estado_de(orden_id)
    exigir(orden["estado"] == "Cerrada" and orden["cerradaEn"], f"la orden no quedó cerrada: {orden}")
    exigir(len(orden["tareas"]) == 1 and len(orden["consumos"]) == 1 and len(orden["hallazgos"]) == 1,
           "faltan tareas, consumos u hallazgos en la orden cerrada")


def abrir_y_poner_en_espera():
    parada = str(uuid.uuid4())
    estado, respuesta = http("POST", API, {
        "paradaId": parada, "paradaProgramada": True, "dronId": "ADV-05", "tipo": "Correctiva", "esTrabajoMayor": False})
    exigir(estado == 201, f"abrir respondió {estado}: {respuesta}")
    orden_id = respuesta["id"]
    verificar_estado(orden_id, "Abierta")
    comando(orden_id, "poner-orden-en-espera", {"motivo": "Esperando repuesto"})
    verificar_estado(orden_id, "EnEspera")


def cierre_llega_a_los_suscriptores(orden_id, parada):
    def recibido():
        estado, mensajes = http("GET", f"{SIM}/received")
        if estado != 200:
            return None
        return [m for m in mensajes if m["topic"] == TOPICO_CERRADA and m["envelope"]["payload"].get("ordenId") == orden_id]

    mensajes = esperar("el simulador recibe 'Orden de trabajo cerrada'", recibido)
    payload = mensajes[0]["envelope"]["payload"]
    exigir(payload["paradaId"] == parada and payload["dronId"] == "ADV-03", f"payload inesperado: {payload}")
    exigir(float(payload["horasHombre"]) == 3.5, f"horasHombre inesperadas: {payload['horasHombre']}")
    exigir([(c["referencia"], c["cantidad"]) for c in payload["consumos"]] == [("HEL-T40", 2)], "consumos inesperados")
    return len(mensajes)


def main():
    print(f"Humo de Intervenciones contra {GATEWAY}")
    parada = str(uuid.uuid4())
    contexto = {}
    paso("la plataforma y el servicio responden", levantar)
    paso("Parada programada abre una orden Abierta", lambda: contexto.update(orden=parada_programada(parada)))
    paso("Faltante detectado pone la orden EnEspera", lambda: faltante_detectado(parada, contexto["orden"]))
    paso("la orden recorre asignar, ejecutar, consumir, hallar, volar, liberar y cerrar",
         lambda: ciclo_de_vida(contexto["orden"]))
    paso("Abrir orden de trabajo y Poner orden en espera por la API", abrir_y_poner_en_espera)
    paso("Orden de trabajo cerrada llega a los suscriptores simulados",
         lambda: contexto.update(entregas=cierre_llega_a_los_suscriptores(contexto["orden"], parada)))
    print(f"\nRESUMEN: {len(PASOS)} pasos correctos; el cierre se entregó {contexto['entregas']} vez/veces al simulador.")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"\nFALLO tras {len(PASOS)} pasos: {error}", file=sys.stderr)
        sys.exit(1)
