#!/usr/bin/env python3
"""Datos de demostración de AgroDrones: se cargan DIRECTAMENTE por la API, a través del gateway.

Con la plataforma levantada (`GATEWAY_PORT=8080 docker compose up --build --wait`):

    python3 seed/seed.py                          # contra http://localhost:8080
    GATEWAY_URL=http://localhost:18080 python3 seed/seed.py

Crea un taller creíble: 8 repuestos con existencias distintas (uno bajo el mínimo, uno con reserva), tres solicitudes de
reposición (abierta, aprobada y cancelada) y seis órdenes de trabajo en seis estados diferentes. Dos de las órdenes nacen
por EVENTO (el plan de mantenimiento programa una parada) para que se vea la integración entre servicios:

  · una parada que pide más hélices de las que hay -> Repuestos avisa del faltante -> la orden queda «En espera»;
  · una parada completa -> la orden se ejecuta, se cierra y Repuestos descuenta el repuesto consumido.

Es idempotente: los identificadores son deterministas y antes de cada paso se mira el estado actual, así que puede correrse
varias veces sin duplicar nada. Para empezar de cero: `docker compose down -v`.
Solo usa la biblioteca estándar.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8080").rstrip("/")
INTERVENCIONES = f"{GATEWAY}/api/intervenciones/orden-de-trabajo"
REPUESTOS = f"{GATEWAY}/api/repuestos"
SIMULADORES = f"{GATEWAY}/sim"
ESPACIO = uuid.UUID("6f0c1c0e-8a53-4b9e-9d57-3f5d2a1c7e10")        # fija: mismos nombres -> mismos identificadores
AHORA = datetime.now(timezone.utc).replace(microsecond=0)


class Fallo(Exception):
    pass


def id_de(nombre: str) -> str:
    return str(uuid.uuid5(ESPACIO, nombre))


def http(metodo: str, url: str, cuerpo=None):
    datos = None if cuerpo is None else json.dumps(cuerpo).encode("utf-8")
    peticion = urllib.request.Request(url, data=datos, method=metodo, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(peticion, timeout=20) as r:
            texto = r.read().decode("utf-8")
            return r.status, (json.loads(texto) if texto else None)
    except urllib.error.HTTPError as e:
        texto = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(texto)
        except ValueError:
            return e.code, {"error": texto}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        raise Fallo(f"no se pudo conectar con {url}: {e}") from e


def exigir(estado: int, esperados, que: str, cuerpo=None):
    if estado not in esperados:
        raise Fallo(f"{que}: HTTP {estado} {cuerpo}")


def esperar(que: str, consulta, segundos: float = 40.0):
    limite = time.time() + segundos
    ultimo = None
    while time.time() < limite:
        ultimo = consulta()
        if ultimo:
            return ultimo
        time.sleep(0.5)
    raise Fallo(f"se agotó la espera: {que}")


RESUMEN: list[str] = []


def paso(texto: str):
    print(f"  ✔ {texto}")


# ======================================================================= Repuestos
# (referencia, descripción, cantidad, stock mínimo, plazo de reposición en días)
CATALOGO = [
    ("HEL-T40", "Hélice plegable T40", 3, 2, 7),
    ("MOT-X8", "Motor sin escobillas X8", 6, 2, 10),
    ("BAT-22K", "Batería inteligente 22 000 mAh", 12, 4, 5),
    ("BOM-12", "Bomba de aspersión 12 L/min", 4, 2, 14),
    ("BOQ-FAN", "Boquilla de abanico", 40, 10, 3),
    ("ESC-60", "Controlador electrónico de velocidad 60 A", 5, 2, 8),
    ("GPS-RTK", "Módulo GPS RTK", 2, 1, 20),
    ("TRD-LIM", "Trípode de aterrizaje (juego)", 8, 3, 6),
]


def existencia(referencia: str):
    estado, cuerpo = http("GET", f"{REPUESTOS}/existencia/{referencia}")
    return cuerpo if estado == 200 else None


def cargar_repuestos():
    print("\nRepuestos del Taller")
    for ref, descripcion, cantidad, minimo, plazo in CATALOGO:
        if existencia(ref):
            paso(f"{ref}: ya existe ({descripcion})")
            continue
        estado, cuerpo = http("POST", f"{REPUESTOS}/existencia", {"referencia": ref, "cantidad": cantidad, "stock_minimo": minimo, "plazo_dias": plazo})
        exigir(estado, (200, 201, 202, 204), f"registrar entrada de {ref}", cuerpo)
        esperar(f"existencia {ref}", lambda ref=ref: existencia(ref))
        paso(f"{ref}: {cantidad} uds · mínimo {minimo} · plazo {plazo} d ({descripcion})")

    # una reserva visible: la OT demo tiene apartadas 2 baterías
    bat = existencia("BAT-22K")
    if bat and not bat.get("reservas"):
        estado, cuerpo = http("POST", f"{REPUESTOS}/existencia/BAT-22K/reservar-repuesto", {"orden_trabajo_id": "OT-DEMO-RESERVA", "cantidad": 2})
        exigir(estado, (200, 201, 202, 204), "reservar baterías", cuerpo)
        paso("BAT-22K: 2 uds reservadas para OT-DEMO-RESERVA")
    else:
        paso("BAT-22K: ya tiene reserva")

    # un ajuste por conteo físico: el almacén contó 38 boquillas y no 40
    boq = existencia("BOQ-FAN")
    if boq and boq.get("fisica") != 38 and boq.get("fisica") == 40:
        estado, cuerpo = http("POST", f"{REPUESTOS}/existencia/BOQ-FAN/ajustar-existencia-por-conteo", {"conteo": 38})
        exigir(estado, (200, 201, 202, 204), "ajustar BOQ-FAN", cuerpo)
        paso("BOQ-FAN: ajustada por conteo físico a 38")

    # solicitudes de reposición en tres estados (identificadores fijos para consultarlas en la interfaz)
    solicitudes = [
        ("solicitud-gps", "GPS-RTK", 2, 4_800_000, None),
        ("solicitud-bomba", "BOM-12", 2, 1_900_000, "aprobar-solicitud"),
        ("solicitud-controlador", "ESC-60", 1, 650_000, "cancelar-solicitud"),
    ]
    for nombre, ref, cantidad, monto, accion in solicitudes:
        sid = id_de(nombre)
        estado, actual = http("GET", f"{REPUESTOS}/solicitud-de-reposicion/{sid}")
        if estado != 200:
            estado, cuerpo = http("POST", f"{REPUESTOS}/solicitud-de-reposicion", {"referencia": ref, "cantidad": cantidad, "monto": monto, "solicitud_id": sid})
            exigir(estado, (200, 201, 202, 204), f"solicitar reposición de {ref}", cuerpo)
            estado, actual = http("GET", f"{REPUESTOS}/solicitud-de-reposicion/{sid}")
        if accion and actual and actual.get("estado") == "abierta":
            estado, cuerpo = http("POST", f"{REPUESTOS}/solicitud-de-reposicion/{sid}/{accion}")
            exigir(estado, (200, 201, 202, 204), f"{accion} {sid}", cuerpo)
            estado, actual = http("GET", f"{REPUESTOS}/solicitud-de-reposicion/{sid}")
        RESUMEN.append(f"  solicitud  {sid}  {ref} x{cantidad}  → {actual.get('estado') if actual else '?'}")
        paso(f"solicitud de {ref} x{cantidad}: {actual.get('estado') if actual else '?'}")


# ======================================================================= Intervenciones
RANGO = {"Abierta": 0, "EnEspera": 1, "EnEjecucion": 2, "Ejecutada": 3, "Liberada": 4, "Cerrada": 5}


def orden_de_parada(parada: str):
    estado, cuerpo = http("GET", f"{INTERVENCIONES}/por-parada/{parada}")
    return cuerpo if estado == 200 and cuerpo else None


def comando(orden: str, nombre: str, cuerpo=None):
    estado, respuesta = http("POST", f"{INTERVENCIONES}/{orden}/{nombre}", cuerpo or {})
    exigir(estado, (200, 201, 202, 204), f"{nombre} sobre {orden}", respuesta)


def orden_completa(orden: str) -> dict:
    estado, cuerpo = http("GET", f"{INTERVENCIONES}/{orden}")
    exigir(estado, (200,), f"consultar la orden {orden}", cuerpo)
    return cuerpo


def estado_de(orden: str) -> str:
    return orden_completa(orden)["estado"]


def avanzar(orden: str, objetivo: str, receta: dict):
    """Lleva la orden hasta `objetivo` ejecutando solo lo que falta, según su estado actual."""
    vuelta = 0
    while RANGO[estado_de(orden)] < RANGO[objetivo] and vuelta < 8:
        vuelta += 1
        actual = estado_de(orden)
        if actual in ("Abierta", "EnEspera") and objetivo == "EnEspera":
            comando(orden, "poner-orden-en-espera", {"motivo": receta["motivo"]})
        elif actual in ("Abierta", "EnEspera"):
            comando(orden, "asignar-tecnico", {"tecnico": receta["tecnico"]})
            tarea = receta["tareas"][0]
            comando(orden, "registrar-ejecucion-de-tarea", {"tareaId": str(uuid.uuid4()), "descripcion": tarea[0], "resultado": tarea[1], "ejecutadaPor": receta["tecnico"], "horas": tarea[2]})
        elif actual == "EnEjecucion":
            # Cada registro se hace solo si la orden todavía no lo tiene: así una corrida interrumpida a medias se reanuda sin duplicar.
            o = orden_completa(orden)
            hechas = {t["descripcion"] for t in o.get("tareas", [])}
            for tarea in receta["tareas"]:
                if tarea[0] not in hechas:
                    comando(orden, "registrar-ejecucion-de-tarea", {"tareaId": str(uuid.uuid4()), "descripcion": tarea[0], "resultado": tarea[1], "ejecutadaPor": receta["tecnico"], "horas": tarea[2]})
            consumidos = {(c["referencia"], c.get("serieInstalada")) for c in o.get("consumos", [])}
            for c in receta.get("consumos", []):
                if (c["referencia"], c.get("serieInstalada")) not in consumidos:
                    comando(orden, "registrar-consumo-de-repuesto", {"consumoId": str(uuid.uuid4()), **c})
            vistos = {h["descripcion"] if isinstance(h, dict) else h for h in o.get("hallazgos", [])}
            for h in receta.get("hallazgos", []):
                if h not in vistos:
                    comando(orden, "registrar-hallazgo", {"descripcion": h})
            v = receta["vuelo"]
            comando(orden, "registrar-vuelo-de-prueba", {"realizadoEn": (AHORA - timedelta(hours=2)).isoformat().replace("+00:00", "Z"),
                                                         "duracionEnMinutos": v[0], "aprobado": True, "observaciones": v[1]})
        elif actual == "Ejecutada":
            comando(orden, "liberar-dron", {"liberacionId": str(uuid.uuid4()), "liberadaPor": receta["liberador"]})
        elif actual == "Liberada":
            comando(orden, "cerrar-orden-de-trabajo")
        else:
            raise Fallo(f"estado inesperado {actual} en la orden {orden}")
    if RANGO[estado_de(orden)] < RANGO[objetivo]:
        raise Fallo(f"la orden {orden} no llegó a {objetivo} (quedó en {estado_de(orden)})")


def abrir_por_api(parada: str, dron: str, tipo: str, mayor: bool) -> str:
    existente = orden_de_parada(parada)
    if existente:
        return existente["id"]
    estado, cuerpo = http("POST", INTERVENCIONES, {"paradaId": parada, "paradaProgramada": True, "dronId": dron, "tipo": tipo, "esTrabajoMayor": mayor})
    exigir(estado, (200, 201), f"abrir la orden de {dron}", cuerpo)
    return cuerpo["id"]


def abrir_por_evento(parada: str, dron: str, tareas: list):
    """El plan de mantenimiento programa una parada: Intervenciones abre la orden y Repuestos reserva (o avisa del faltante)."""
    existente = orden_de_parada(parada)
    if existente:
        return existente["id"]
    carga = {"paradaId": parada, "dronId": dron, "fechaProgramada": (AHORA + timedelta(days=3)).isoformat().replace("+00:00", "Z"), "tareas": tareas}
    estado, cuerpo = http("POST", f"{SIMULADORES}/simulate/plan-de-mantenimiento/parada-programada", carga)
    exigir(estado, (200, 202), f"publicar la parada de {dron}", cuerpo)
    return esperar(f"la parada de {dron} abre una orden", lambda: (orden_de_parada(parada) or {}).get("id"))


ORDENES = [
    # nombre, dron, tipo, mayor, origen, objetivo, receta
    dict(nombre="ADV-01", dron="ADV-01", tipo="Preventiva", mayor=False, origen="api", objetivo="Abierta", receta={}),
    dict(nombre="ADV-02", dron="ADV-02", origen="evento", objetivo="EnEspera", receta={},
         tareas_evento=[{"tareaId": "T-201", "descripcion": "Cambio de hélices", "repuestos": [{"referencia": "HEL-T40", "cantidad": 5}]}]),
    dict(nombre="ADV-03", dron="ADV-03", tipo="Preventiva", mayor=False, origen="api", objetivo="EnEjecucion",
         receta=dict(tecnico="Ana", tareas=[("Inspección de motores y hélices", "Realizada", 2.5)])),
    dict(nombre="ADV-04", dron="ADV-04", tipo="PorCondicion", mayor=False, origen="api", objetivo="Ejecutada",
         receta=dict(tecnico="Carlos", tareas=[("Limpieza y calibración de boquillas", "Realizada", 1.5)],
                     consumos=[dict(referencia="BOQ-FAN", cantidad=4, requiereSerie=False, serieRetirada=None, serieInstalada=None, horaDeCorte=None)],
                     hallazgos=["Boquilla 3 con obstrucción parcial"], vuelo=(6, "Aspersión uniforme"))),
    dict(nombre="ADV-05", dron="ADV-05", tipo="Correctiva", mayor=True, origen="api", objetivo="Liberada",
         receta=dict(tecnico="Ana", liberador="Beto", tareas=[("Reemplazo del motor M3", "Realizada", 6.0)],
                     consumos=[dict(referencia="MOT-X8", cantidad=1, requiereSerie=True, serieRetirada="MX8-0412", serieInstalada="MX8-0987", horaDeCorte=412)],
                     hallazgos=["Rodamiento del motor M3 con holgura"], vuelo=(9, "Sin vibraciones tras el cambio"))),
    dict(nombre="ADV-06", dron="ADV-06", origen="evento", objetivo="Cerrada",
         tareas_evento=[{"tareaId": "T-601", "descripcion": "Revisión de la bomba", "repuestos": [{"referencia": "BOM-12", "cantidad": 1}]}],
         receta=dict(tecnico="Carlos", liberador="Beto", tareas=[("Revisión de la bomba", "Realizada", 2.0)],
                     consumos=[dict(referencia="BOM-12", cantidad=1, requiereSerie=False, serieRetirada=None, serieInstalada=None, horaDeCorte=None)],
                     hallazgos=[], vuelo=(8, "Presión estable"))),
]


def cargar_ordenes():
    print("\nIntervenciones")
    for o in ORDENES:
        parada = id_de(f"parada-{o['nombre']}")
        orden = abrir_por_api(parada, o["dron"], o["tipo"], o["mayor"]) if o["origen"] == "api" else abrir_por_evento(parada, o["dron"], o["tareas_evento"])
        if o["objetivo"] == "EnEspera" and o["origen"] == "evento":
            esperar(f"el faltante pone en espera la orden de {o['dron']}", lambda orden=orden: estado_de(orden) == "EnEspera")
        else:
            avanzar(orden, o["objetivo"], o["receta"])
        estado = estado_de(orden)
        via = "por evento" if o["origen"] == "evento" else "por API"
        RESUMEN.append(f"  orden      {orden}  {o['dron']}  → {estado}")
        paso(f"{o['dron']}: {estado} ({via})")


def verificar_integracion():
    """Lo que debe haber pasado entre servicios: faltante de hélices y consumo de la bomba tras cerrar ADV-06."""
    hel = existencia("HEL-T40")
    bom = existencia("BOM-12")
    print("\nIntegración entre servicios")
    esperar("el cierre de ADV-06 descuenta la bomba", lambda: (existencia("BOM-12") or {}).get("fisica") == 3, 25)
    paso(f"HEL-T40 sigue en {hel['fisica']} uds (la parada pedía 5: Repuestos avisó del faltante y la orden de ADV-02 quedó en espera)")
    paso("BOM-12 bajó de 4 a 3 uds: al cerrarse ADV-06, Intervenciones publicó el cierre y Repuestos confirmó el consumo")
    return bom


def main() -> int:
    print(f"Cargando datos de demostración en {GATEWAY}")
    try:
        esperar("el servicio de Repuestos responde", lambda: http("GET", f"{REPUESTOS}/health")[0] == 200, 60)
        esperar("el servicio de Intervenciones responde", lambda: 0 < http("GET", f"{INTERVENCIONES}/por-parada/{uuid.uuid4()}")[0] < 500, 60)
        esperar("los simuladores responden", lambda: http("GET", f"{SIMULADORES}/health")[0] == 200, 60)
        cargar_repuestos()
        cargar_ordenes()
        verificar_integracion()
    except Fallo as error:
        print(f"\nFALLO: {error}", file=sys.stderr)
        return 1
    print("\nListo. Identificadores para probar en la interfaz (pégalos en las consultas):")
    print("\n".join(RESUMEN))
    print(f"\nInterfaz: {GATEWAY}/   ·   repuestos: " + ", ".join(c[0] for c in CATALOGO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
