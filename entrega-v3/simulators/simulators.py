"""Simuladores de los contextos que NO se implementan (interoperabilidad simulada). Solo biblioteca estándar.
- Reciben eventos: POST /events/{topic}         (GET /received para inspeccionarlos)
- Emiten eventos:  POST /simulate/{contexto}/{evento}   (cuerpo opcional: sustituye al ejemplo)
- APIs síncronas:  GET|POST /api/{contexto}/{operacion}[/...]  -> respuesta simulada
"""
import json, os, urllib.request, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CFG = json.load(open(os.environ.get("SIM_FILE", "simulators.json"), encoding="utf-8"))
BUS = os.environ.get("BUS_URL", "http://event-bus:5100")
RECEIVED = []


class H(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(n)) if n else None
        except Exception:
            return None

    def do_GET(self):
        p = self.path.split("?")[0].strip("/").split("/")
        if p == ["health"]:
            return self._send(200, {"status": "ok"})
        if p == ["received"]:
            return self._send(200, RECEIVED)
        if p[:1] == ["api"]:
            return self._api(p, None)
        self._send(404, {"error": "no existe"})

    def do_POST(self):
        p = self.path.split("?")[0].strip("/").split("/")
        body = self._body()
        if p[:1] == ["events"] and len(p) == 2:
            RECEIVED.append({"topic": p[1], "envelope": body, "recibidoEn": datetime.now(timezone.utc).isoformat()})
            return self._send(200, {"recibido": True})
        if p[:1] == ["simulate"] and len(p) == 3:
            return self._simulate(p[1], p[2], body)
        if p[:1] == ["api"]:
            return self._api(p, body)
        self._send(404, {"error": "no existe"})

    def _simulate(self, ctx, ev, body):
        spec = next((e for e in CFG["emits"] if e["context_slug"] == ctx and e["event_slug"] == ev), None)
        if not spec:
            return self._send(404, {"error": "el simulador no emite ese evento", "disponibles": [f"{e['context_slug']}/{e['event_slug']}" for e in CFG["emits"]]})
        env = {"eventId": str(uuid.uuid4()), "topic": spec["topic"], "occurredOn": datetime.now(timezone.utc).isoformat(),
               "correlationId": str(uuid.uuid4()), "payload": body or spec["sample"]}
        req = urllib.request.Request(BUS + "/publish", json.dumps(env).encode(), {"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return self._send(202, {"publicado": env, "bus": r.status})
        except Exception as e:
            return self._send(502, {"error": f"el bus no respondió: {e}"})

    def _api(self, p, body):
        ctx, op = (p + ["", ""])[1], (p + ["", "", ""])[2]
        known = [a for a in CFG["apis"] if a["context_slug"] == ctx and a["operation_slug"] == op]
        if not known:
            return self._send(404, {"error": "API simulada desconocida", "disponibles": [f"/api/{a['context_slug']}/{a['operation_slug']}" for a in CFG["apis"]]})
        self._send(200, {"ok": True, "simulado": True, "contexto": known[0]["context"], "operacion": known[0]["operation"],
                         "habilitado": True, "ruta": "/".join(p), "eco": body})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "5110"))), H).serve_forever()
