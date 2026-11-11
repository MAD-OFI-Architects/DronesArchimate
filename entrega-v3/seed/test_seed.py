"""Pruebas herméticas del script de datos de demostración (sin Docker): una API falsa con las reglas reales de los servicios.

    python3 -m unittest seed/test_seed.py -v
"""
import copy
import importlib.util
import io
import re
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ESPEC = importlib.util.spec_from_file_location("seed", Path(__file__).with_name("seed.py"))
seed = importlib.util.module_from_spec(ESPEC)
ESPEC.loader.exec_module(seed)
RANGO = seed.RANGO


class ApiFalsa:
    """Reglas copiadas de los servicios: vuelo 5–10 min, liberar solo Ejecutada, trabajo mayor lo firma otra persona, cerrar descuenta stock."""

    def __init__(self):
        self.ordenes: dict[str, dict] = {}
        self.paradas: dict[str, str] = {}
        self.stock: dict[str, dict] = {}
        self.solicitudes: dict[str, dict] = {}
        self.fallar_vuelo_una_vez = None          # dron cuyo primer vuelo devuelve 400 (simula una corrida interrumpida)
        self.llamadas = 0

    def _orden(self, parada, dron, tipo="Preventiva", mayor=False, estado="Abierta"):
        oid = str(uuid.uuid4())
        self.ordenes[oid] = dict(id=oid, dronId=dron, tipo=tipo, esTrabajoMayor=mayor, estado=estado, tecnico=None, tareas=[], consumos=[], hallazgos=[], vuelos=[])
        self.paradas[parada] = oid
        return oid

    def __call__(self, metodo, url, cuerpo=None):
        self.llamadas += 1
        ruta = url.replace(seed.GATEWAY, "")
        if ruta in ("/api/repuestos/health", "/sim/health"):
            return 200, {"status": "ok"}
        if ruta.startswith("/sim/simulate/plan-de-mantenimiento/parada-programada"):
            p = cuerpo
            faltante = any(self.stock.get(r["referencia"], {"fisica": 0})["fisica"] < r["cantidad"] for t in p["tareas"] for r in t["repuestos"])
            if p["paradaId"] not in self.paradas:
                self._orden(p["paradaId"], p["dronId"], estado="EnEspera" if faltante else "Abierta")
            return 202, {}
        if ruta.startswith("/api/intervenciones/orden-de-trabajo"):
            return self._intervenciones(metodo, ruta.split("orden-de-trabajo", 1)[1], cuerpo)
        if ruta.startswith("/api/repuestos/"):
            return self._repuestos(metodo, ruta[len("/api/repuestos/"):], cuerpo)
        return 404, {"error": ruta}

    def _intervenciones(self, metodo, resto, c):
        if resto == "" and metodo == "POST":
            if c["paradaId"] in self.paradas:
                return 409, {}
            return 201, {"id": self._orden(c["paradaId"], c["dronId"], c["tipo"], c["esTrabajoMayor"])}
        m = re.match(r"/por-parada/(.+)", resto)
        if m:
            oid = self.paradas.get(m.group(1))
            return (200, copy.deepcopy(self.ordenes[oid])) if oid else (404, {})
        m = re.match(r"/([^/]+)(?:/(.+))?", resto)
        o = self.ordenes.get(m.group(1))
        if not o:
            return 404, {}
        cmd = m.group(2)
        if cmd is None:
            return 200, copy.deepcopy(o)
        if cmd == "poner-orden-en-espera":
            o["estado"] = "EnEspera"
        elif cmd == "asignar-tecnico":
            o["tecnico"] = c["tecnico"]
        elif cmd == "registrar-ejecucion-de-tarea":
            o["tareas"].append(dict(c))
            o["estado"] = "EnEjecucion"
        elif cmd == "registrar-consumo-de-repuesto":
            o["consumos"].append(dict(c))
        elif cmd == "registrar-hallazgo":
            o["hallazgos"].append(dict(c))
        elif cmd == "registrar-vuelo-de-prueba":
            if self.fallar_vuelo_una_vez == o["dronId"]:
                self.fallar_vuelo_una_vez = None
                return 400, {"detail": "fallo inyectado"}
            if not 5 <= c["duracionEnMinutos"] <= 10:
                return 400, {"detail": "El campo 'DuracionEnMinutos' debe estar entre 5 y 10."}
            o["vuelos"].append(dict(c))
            o["estado"] = "Ejecutada"
        elif cmd == "liberar-dron":
            if o["estado"] != "Ejecutada" or (o["esTrabajoMayor"] and c["liberadaPor"] in {t["ejecutadaPor"] for t in o["tareas"]}):
                return 422, {}
            o["estado"] = "Liberada"
        elif cmd == "cerrar-orden-de-trabajo":
            if o["estado"] != "Liberada":
                return 422, {}
            o["estado"] = "Cerrada"
            for k in o["consumos"]:                       # Repuestos confirma el consumo al recibir el cierre
                if k["referencia"] in self.stock:
                    self.stock[k["referencia"]]["fisica"] -= k["cantidad"]
        else:
            return 404, {}
        return 204, None

    def _repuestos(self, metodo, resto, c):
        if resto == "existencia" and metodo == "POST":
            self.stock[c["referencia"]] = dict(referencia=c["referencia"], fisica=c["cantidad"], estado="disponible", reservas=[])
            return 201, {}
        m = re.match(r"existencia/([^/]+)(?:/(.+))?", resto)
        if m:
            e = self.stock.get(m.group(1))
            if not e:
                return 404, {}
            cmd = m.group(2)
            if cmd is None:
                return 200, copy.deepcopy(e)
            if cmd == "reservar-repuesto":
                e["reservas"].append(dict(c))
                e["estado"] = "reservado"
            elif cmd == "ajustar-existencia-por-conteo":
                e["fisica"] = c["conteo"]
            return 204, None
        if resto == "solicitud-de-reposicion" and metodo == "POST":
            self.solicitudes[c["solicitud_id"]] = dict(c, estado="abierta")
            return 201, {}
        m = re.match(r"solicitud-de-reposicion/([^/]+)(?:/(.+))?", resto)
        if m:
            s = self.solicitudes.get(m.group(1))
            if not s:
                return 404, {}
            if m.group(2) == "aprobar-solicitud":
                s["estado"] = "aprobada"
            elif m.group(2) == "cancelar-solicitud":
                s["estado"] = "cancelada"
            return (200, copy.deepcopy(s)) if m.group(2) is None else (204, None)
        return 404, {}


class PruebasDelSeed(unittest.TestCase):
    def setUp(self):
        self.api = ApiFalsa()
        self.originales = (seed.http, seed.time.sleep, seed.RESUMEN[:])
        seed.http = self.api
        seed.time.sleep = lambda _s: None
        seed.RESUMEN.clear()

    def tearDown(self):
        seed.http, seed.time.sleep = self.originales[0], self.originales[1]

    def correr(self):
        seed.RESUMEN.clear()
        salida, error = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(error):
            codigo = seed.main()
        return codigo, salida.getvalue(), error.getvalue()

    def estados(self):
        return sorted((o["dronId"], o["estado"]) for o in self.api.ordenes.values())

    def test_una_corrida_deja_seis_ordenes_en_seis_estados_y_las_solicitudes(self):
        codigo, _, error = self.correr()
        self.assertEqual(codigo, 0, error)
        self.assertEqual(self.estados(), [("ADV-01", "Abierta"), ("ADV-02", "EnEspera"), ("ADV-03", "EnEjecucion"),
                                          ("ADV-04", "Ejecutada"), ("ADV-05", "Liberada"), ("ADV-06", "Cerrada")])
        self.assertEqual(sorted(s["estado"] for s in self.api.solicitudes.values()), ["abierta", "aprobada", "cancelada"])
        self.assertEqual(len(self.api.stock), 8)
        self.assertEqual(self.api.stock["BOM-12"]["fisica"], 3)                 # el cierre de ADV-06 descontó la bomba
        self.assertEqual(self.api.stock["BOQ-FAN"]["fisica"], 38)               # el ajuste por conteo
        self.assertEqual(len(self.api.stock["BAT-22K"]["reservas"]), 1)

    def test_repetirla_no_cambia_nada(self):
        self.correr()
        antes = copy.deepcopy((self.api.ordenes, self.api.stock, self.api.solicitudes))
        codigo, _, error = self.correr()
        self.assertEqual(codigo, 0, error)
        self.assertEqual(copy.deepcopy((self.api.ordenes, self.api.stock, self.api.solicitudes)), antes)

    def test_una_corrida_interrumpida_a_medias_se_reanuda_sin_duplicar(self):
        self.api.fallar_vuelo_una_vez = "ADV-05"                                # el vuelo falla DESPUÉS de registrar consumo y hallazgo
        codigo, _, error = self.correr()
        self.assertEqual(codigo, 1)
        self.assertIn("fallo inyectado", error)
        codigo, _, error = self.correr()
        self.assertEqual(codigo, 0, error)
        adv5 = next(o for o in self.api.ordenes.values() if o["dronId"] == "ADV-05")
        self.assertEqual((adv5["estado"], len(adv5["tareas"]), len(adv5["consumos"]), len(adv5["hallazgos"])), ("Liberada", 1, 1, 1))

    def test_los_vuelos_respetan_el_rango_que_exige_el_servicio(self):
        for o in seed.ORDENES:
            vuelo = o["receta"].get("vuelo")
            if vuelo:
                self.assertTrue(5 <= vuelo[0] <= 10, f"{o['nombre']}: {vuelo[0]} min fuera de 5–10")

    def test_en_trabajo_mayor_quien_libera_no_es_quien_ejecuto(self):
        for o in seed.ORDENES:
            if o.get("mayor"):
                self.assertNotEqual(o["receta"]["tecnico"], o["receta"]["liberador"])

    def test_si_el_servicio_no_responde_falla_con_un_mensaje_claro(self):
        seed.http = lambda *_a, **_k: (_ for _ in ()).throw(seed.Fallo("no se pudo conectar"))
        seed.esperar.__defaults__ = (0.01,)
        try:
            codigo, _, error = self.correr()
        finally:
            seed.esperar.__defaults__ = (40.0,)
        self.assertEqual(codigo, 1)
        self.assertIn("FALLO", error)


if __name__ == "__main__":
    unittest.main()
