"""Etapa 2 (determinista): todo lo que NO necesita un LLM.

Genera: contrato del bus, bus de eventos, simuladores de los demás contextos, docker-compose,
esqueleto de microfrontends (Web Components) y las instrucciones de proyecto para los agentes.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import eventcontracts, interconexion
from .config import Config
from .util import kebab, pascal

BUS_PORT, SIM_PORT, GATEWAY_PORT = 5100, 5110, 8080

SKELETONS = Path(__file__).parent / "skeletons"
MARCA_DURABLE = "ARCHIFORGE: mensajeria-durable"


# ----------------------------------------------------------------------------- topics
def topic(context: str, event: str) -> str:
    return f"{kebab(context)}.{kebab(event)}.v1"


def bus_topics(ir: dict, cfg: Config, manifest: dict) -> dict:
    ctx = {c["name"]: c for c in ir["contexts"]}
    api_events = {e for r in ir["context_relations"] if r["mechanism"].startswith("API") for e in r["events"]}
    real = {d.context: d for d in cfg.domains}
    table = eventcontracts.load(cfg.tool_root)
    topics = []
    for c in ir["contexts"]:
        for ev in c["published_events"]:
            if ev in api_events:
                continue
            subs = []
            for o in ir["contexts"]:
                if o["name"] != c["name"] and ev in o["consumed_events"]:
                    if o["name"] not in real and c["name"] not in real:
                        continue          # simulado -> simulado: fuera del alcance
                    if o["name"] in real:
                        d = real[o["name"]]
                        url = f"http://{d.slug}:{d.port}/events/{topic(c['name'], ev)}"
                    else:
                        url = f"http://simulators:{SIM_PORT}/events/{topic(c['name'], ev)}"
                    subs.append({"context": o["name"], "url": url})
            if subs:
                spec = eventcontracts.for_event(table, ev)
                topics.append({"topic": topic(c["name"], ev), "event": ev, "publisher": c["name"],
                               "publisher_real": c["name"] in real, "subscribers": subs,
                               "description": spec["descripcion"], "payload": spec["payload"], "sample": spec["sample"]})
    return {"topics": topics}


# ----------------------------------------------------------------------------- docs
def mensajeria(cfg: Config, bt: dict) -> str:
    """Canal de eventos decidido por el arquitecto. Si el modelo tiene eventos entre contextos y no se decidió, no se elige por él."""
    m = cfg.platform.get("mensajeria")
    if m is None and bt["topics"]:
        from .decisions import MENSAJERIAS
        raise SystemExit("Falta decidir el canal de eventos de la plataforma (el modelo tiene eventos entre contextos). "
                         "Decide uno con `python -m forge platform --messaging <opción>`:\n" +
                         "\n".join(f"  · {k}: {v}" for k, v in MENSAJERIAS.items()))
    return m or "memoria"


def gateway(cfg: Config, with_frontend: bool) -> str:
    """Gateway decidido por el arquitecto. La plataforma de humo por dominio (sin frontend) es interna de la herramienta: siempre nginx."""
    if not with_frontend:
        return "nginx"
    g = cfg.platform.get("gateway")
    if g is None:
        from .decisions import GATEWAYS
        raise SystemExit("Falta decidir el gateway de la plataforma. Decide uno con `python -m forge platform --gateway <opción>`:\n" +
                         "\n".join(f"  · {k}: {v}" for k, v in GATEWAYS.items()))
    return g


def contract_doc(ir: dict, cfg: Config, manifest: dict, bt: dict) -> str:
    L = ["# Contrato del bus de eventos y de las APIs de interoperabilidad", "",
         "> Contract-first: este documento manda sobre los servicios. Los **campos de cada evento son supuestos de diseño** "
         "(el modelo ArchiMate nombra los eventos pero no define su carga útil); se ajustan en `config/event-payloads.json` del orquestador.", "",
         "## Sobre (envelope) — JSON", "```json",
         json.dumps({"eventId": "uuid (el mismo del evento de dominio; clave de idempotencia)", "topic": "<contexto>.<evento>.v1",
                     "occurredOn": "ISO 8601 UTC", "correlationId": "uuid", "payload": {"…": "según el tópico"}}, indent=2, ensure_ascii=False),
         "```", "",
         f"- Publicar: `POST http://event-bus:{BUS_PORT}/publish` con el sobre.",
         "- Recibir: cada servicio expone `POST /events/{topic}` (el bus lo llama con el mismo sobre; responde 2xx si procesó **o** si ya lo había procesado).",
         "- Entrega **al menos una vez** con reintentos: los consumidores DEBEN ser idempotentes por `eventId`.",
         *(["- El bus guarda los mensajes en RabbitMQ (colas durables, una por tópico y suscriptor): sobreviven a reinicios del bus y del suscriptor.",
            "- Si el suscriptor no responde 2xx, el mensaje se reintenta tras una espera; agotados los intentos queda en la cola de mensajes muertos (`GET /dlq`, `POST /dlq/reprocesar`).",
            "- `POST /publish` responde **202** cuando el broker confirmó el mensaje y **503** si no está disponible: el emisor reintenta desde su bandeja de salida."]
           if mensajeria(cfg, bt) == "rabbitmq" else
           ["- El bus es un relé HTTP en memoria: reintenta la entrega con espera creciente, pero no conserva los mensajes si se reinicia."]), "",
         "## Tópicos", "", "| Tópico | Publica | Suscriptores | Descripción |", "|---|---|---|---|"]
    for t in bt["topics"]:
        L.append(f"| `{t['topic']}` | {t['publisher']}{' (real)' if t['publisher_real'] else ' (simulado)'} | "
                 f"{', '.join(s['context'] for s in t['subscribers'])} | {t['description']} |")
    for t in bt["topics"]:
        L += ["", f"### `{t['topic']}`", "Campos del `payload`:", "```json", json.dumps(t["payload"], indent=2, ensure_ascii=False),
              "```", "Ejemplo:", "```json", json.dumps(t["sample"], indent=2, ensure_ascii=False), "```"]
    L += ["", "## APIs síncronas entre contextos (capa anticorrupción)", "",
          "El consumidor lee `<PROVEEDOR>_API_URL` y llama a `<URL>/<operación>`; el compose decide si esa URL es el servicio real del proveedor "
          "o su simulador, así que el consumidor no cambia cuando el proveedor se construye.", "",
          "| Consumidor | Proveedor | Estado del proveedor | Variable de entorno | Llamada |", "|---|---|---|---|---|"]
    real_ctx = {d.context for d in cfg.domains}
    for ctx_name, info in manifest["domains"].items():
        for a in info["acl"]:
            estado = "real" if a["upstream"] in real_ctx else "simulado"
            L.append(f"| {ctx_name} | {a['upstream']} | {estado} | `{a['env']}` | `POST {{{a['env']}}}/{a['slug']}` · {a['mechanism']} |")
    L += ["", "Un proveedor **real** debe exponer `POST /api/<operación>` para cada operación con nombre que declara el modelo; un proveedor "
          "simulado la sirve en `/api/<contexto>/<operación>` del simulador.", "",
          f"El gateway (`http://localhost:{GATEWAY_PORT}`) expone: `/api/<servicio>/…` → servicios reales, `/sim/…` → simuladores. "
          "Dentro de la red de Docker cada servicio recibe sus URL por variables de entorno.", ""]
    return "\n".join(L)


# ----------------------------------------------------------------------------- código de bus y simuladores
BUS_PY = (SKELETONS / "bus.py.tmpl").read_text(encoding="utf-8")

SIM_PY = r'''"""Simuladores de los contextos que NO se implementan (interoperabilidad simulada). Solo biblioteca estándar.
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
'''

BUS_DOCKER = '''FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "bus.py"]
'''

PY_DOCKER = '''FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "{script}"]
'''


BUS_README_MEMORIA = """# Bus de eventos por tópicos (relé HTTP en memoria)

Los servicios publican con `POST /publish` y el bus entrega a cada suscriptor por `POST /events/{topic}`, con reintentos y
espera creciente. No usa broker: **no conserva los mensajes en vuelo si se reinicia**. Contrato: `../docs/contrato-bus.md`.
Para mensajes durables y cola de mensajes muertos, decide `mensajeria = "rabbitmq"` (`python -m forge platform`).
"""

BUS_README = """# Bus de eventos por tópicos (sobre RabbitMQ)

Los servicios publican con `POST /publish` y reciben con `POST /events/{topic}`; entre ambos, RabbitMQ guarda los mensajes.
Contrato: `../docs/contrato-bus.md`.

- Por cada (tópico, suscriptor) hay una cola durable `<tópico>::<contexto>`, una cola de espera `.retry` y una cola de
  mensajes muertos `.dlq`. Tras `BUS_MAX_INTENTOS` (5) entregas fallidas el mensaje queda en la `.dlq`.
- `GET /dlq` cuenta los mensajes muertos por cola; `POST /dlq/reprocesar` los devuelve a su cola principal.
- `GET /events` muestra las últimas publicaciones; `GET /topics`, el catálogo.
- Consola de RabbitMQ: `http://localhost:${RABBITMQ_UI_PORT:-15672}` (usuario y clave `guest`).
- Sin `RABBITMQ_URL` el bus trabaja en memoria (solo pruebas): no conserva nada al reiniciarse.
"""


def _compose(cfg: Config, bt: dict, services_rel: str, with_frontend: bool, ir: dict | None = None) -> tuple[str, str]:
    """(docker-compose.yml, init-postgres.sql). services_rel: ruta de los servicios respecto al compose."""
    from .manifest import service_env
    py_hc = ('["CMD", "python", "-c", "import urllib.request;urllib.request.urlopen(\'http://localhost:%d/health\')"]')
    L = ["# Generado por ArchiForge (forge assemble / smoke por dominio). Levantar: docker compose up --build   (gateway: http://localhost:${GATEWAY_PORT:-%d})" % GATEWAY_PORT,
         "name: ${COMPOSE_PROJECT:-drones-mantenimiento}", "services:"]
    dbs = {d.database for d in cfg.domains}
    if "mongodb" in dbs:
        L.append("  mongo:\n    image: mongo:7\n    command: [\"--replSet\", \"rs0\", \"--bind_ip_all\"]\n    healthcheck:\n      test: [\"CMD\", \"mongosh\", \"--quiet\", \"--eval\", "
                 "\"try { rs.status().ok } catch (e) { rs.initiate({_id:'rs0',members:[{_id:0,host:'mongo:27017'}]}).ok }\"]\n      interval: 5s\n      timeout: 5s\n      retries: 20")
    if "postgresql" in dbs:
        L.append("  postgres:\n    image: postgres:16\n    environment:\n      POSTGRES_USER: forge\n      POSTGRES_PASSWORD: forge\n      POSTGRES_DB: forge\n"
                 "    volumes:\n      - ./init-postgres.sql:/docker-entrypoint-initdb.d/init.sql:ro\n    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U forge -d forge\"]\n      interval: 5s\n      timeout: 5s\n      retries: 20")
    rabbit = mensajeria(cfg, bt) == "rabbitmq"
    if rabbit:
        L.append("  rabbitmq:\n    image: rabbitmq:3.13-management-alpine\n    ports:\n      - \"${RABBITMQ_UI_PORT:-15672}:15672\"\n    healthcheck:\n      test: [\"CMD\", \"rabbitmq-diagnostics\", \"-q\", \"ping\"]\n      interval: 5s\n      timeout: 10s\n      retries: 20")
    espera_broker = "\n      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/\n    depends_on:\n      rabbitmq:\n        condition: service_healthy" if rabbit else ""
    L += [f"  event-bus:\n    build: ./event-bus\n    environment:\n      PORT: \"{BUS_PORT}\"\n      TOPICS_FILE: /app/topics.json{espera_broker}\n    healthcheck:\n      test: {py_hc % BUS_PORT}\n      interval: 5s\n      timeout: 5s\n      retries: 20",
          f"  simulators:\n    build: ./simulators\n    environment:\n      PORT: \"{SIM_PORT}\"\n      BUS_URL: http://event-bus:{BUS_PORT}\n    depends_on:\n      event-bus:\n        condition: service_healthy\n    healthcheck:\n      test: {py_hc % SIM_PORT}\n      interval: 5s\n      timeout: 5s\n      retries: 20"]
    for d in cfg.domains:
        env = service_env(d, BUS_PORT, SIM_PORT, api_urls=interconexion.api_urls(ir, d, cfg.domains, SIM_PORT) if ir else None)
        dep = "mongo" if d.database == "mongodb" else "postgres"
        L.append(f"  {d.slug}:\n    build: {services_rel}/{d.slug}\n    environment:\n" + "\n".join(f'      {k}: "{v}"' for k, v in env.items()) +
                 f"\n    depends_on:\n      {dep}:\n        condition: service_healthy\n      event-bus:\n        condition: service_healthy")
    deps = "\n      - ".join([d.slug for d in cfg.domains] + ["simulators"])
    if gateway(cfg, with_frontend) == "propio":
        # sin gateway generado: cada servicio publica su puerto para que el gateway del equipo los enrute
        for d in cfg.domains:
            i = next(i for i, x in enumerate(L) if x.startswith(f"  {d.slug}:\n"))
            L[i] = L[i].replace("\n    environment:", f"\n    ports:\n      - \"{d.port}:{d.port}\"\n    environment:", 1)
    elif with_frontend:
        L.append(f"  gateway:\n    build: ./frontend\n    ports:\n      - \"${{GATEWAY_PORT:-{GATEWAY_PORT}}}:80\"\n    depends_on:\n      - {deps}")
    else:      # smoke por dominio: solo el proxy; el microfrontend se verifica con su propio build y pruebas
        L.append(f"  gateway:\n    image: nginx:1.27-alpine\n    volumes:\n      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro\n    ports:\n      - \"${{GATEWAY_PORT:-{GATEWAY_PORT}}}:80\"\n    depends_on:\n      - {deps}")
    sql = "\n".join(f"CREATE DATABASE {d.slug.replace('-', '_')};" for d in cfg.domains if d.database == "postgresql") + "\n"
    return "\n".join(L) + "\n", sql


def gateway_doc(cfg: Config) -> str:
    """Rutas que el frontend y las demás piezas esperan, para quien configure su propio gateway."""
    L = ["# Rutas del gateway", "",
         "El generador no incluye gateway: el equipo configura el suyo (Kong, Traefik, un balanceador de la nube, etc.) con estas rutas.", "",
         "## Hacia los servicios", "", "| Ruta pública | Destino |", "|---|---|"]
    for d in cfg.domains:
        L.append(f"| `/api/{kebab(d.context).split('-')[0]}/…` | `http://{d.slug}:{d.port}/api/…` (puerto publicado: `{d.port}`) |")
    L += [f"| `/sim/…` | `http://simulators:{SIM_PORT}/` |", f"| `/bus/…` | `http://event-bus:{BUS_PORT}/` |", "",
          "## Frontend", "",
          "Cada microfrontend se construye con `npm run build` en su carpeta (`frontend/mfe-*`). El gateway o un servidor estático debe servir:", "",
          "- `/` → `frontend/mfe-shell/dist` (con `index.html` como respaldo de las rutas de la aplicación).",
          "- `/mfe/<etiqueta>/<etiqueta>.js` → `frontend/<etiqueta>/dist/<etiqueta>.js` de cada remote.",
          "- `/mfe-manifest.json` → el del shell.", ""]
    return "\n".join(L)


def _nginx(cfg: Config) -> str:
    loc = []
    for d in cfg.domains:
        short = kebab(d.context).split("-")[0]
        loc.append(f"  location /api/{short}/ {{ proxy_pass http://{d.slug}:{d.port}/api/; proxy_set_header Host $host; }}")
    return ("server {\n  listen 80;\n  root /usr/share/nginx/html;\n  index index.html;\n" + "\n".join(loc) +
             f"\n  location /sim/ {{ proxy_pass http://simulators:{SIM_PORT}/; }}\n  location /bus/ {{ proxy_pass http://event-bus:{BUS_PORT}/; }}\n  location /mfe/ {{ add_header Cache-Control no-cache; }}\n"
            "  location / { try_files $uri /index.html; }\n}\n")


# ----------------------------------------------------------------------------- frontend
REMOTE_PKG = {
    "private": True, "type": "module",
    "scripts": {"dev": "vite", "build": "tsc --noEmit && vite build", "test": "vitest run"},
    "dependencies": {"react": "^18.3.1", "react-dom": "^18.3.1"},
    "devDependencies": {"@types/react": "^18.3.3", "@types/react-dom": "^18.3.0", "@vitejs/plugin-react": "^4.3.1",
                        "typescript": "^5.5.4", "vite": "^5.4.2", "vitest": "^2.0.5", "jsdom": "^25.0.0",
                        "@testing-library/react": "^16.0.0", "@testing-library/jest-dom": "^6.4.8", "@testing-library/user-event": "^14.5.2"},
}
VITE_REMOTE = """import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Cada remote se publica como UN módulo ES que registra un custom element (Web Component).
export default defineConfig({
  plugins: [react()],
  define: { 'process.env.NODE_ENV': '"production"' },
  build: { lib: { entry: 'src/main.tsx', formats: ['es'], fileName: () => '__SLUG__.js' }, cssCodeSplit: false },
  test: { environment: 'jsdom', globals: true, setupFiles: ['./src/setup-tests.ts'] },
});
"""
TSCONFIG = json.dumps({"compilerOptions": {"target": "ES2020", "lib": ["ES2020", "DOM", "DOM.Iterable"], "module": "ESNext",
                                           "moduleResolution": "bundler", "jsx": "react-jsx", "strict": True, "skipLibCheck": True,
                                           "noEmit": True, "types": ["vite/client", "vitest/globals"]}, "include": ["src"]}, indent=2)
MAIN_TSX = """import { createRoot, type Root } from 'react-dom/client';
import { App } from './App';
import css from './styles.css?inline';

class Element extends HTMLElement {
  private root?: Root;
  connectedCallback() {
    const shadow = this.shadowRoot ?? this.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = css;
    const mount = document.createElement('div');
    shadow.replaceChildren(style, mount);
    this.root = createRoot(mount);
    this.root.render(<App role={this.getAttribute('data-role') ?? ''} />);
  }
  disconnectedCallback() { this.root?.unmount(); }
}
if (!customElements.get('__SLUG__')) customElements.define('__SLUG__', Element);
"""
API_TS = """// Cliente HTTP común del remote. Todo pasa por el gateway (/api/<servicio>/…).
export interface Problem { title?: string; detail?: string; regla?: string; status?: number }
export class ApiError extends Error {
  constructor(public problem: Problem) { super(problem.detail ?? problem.title ?? 'Error'); }
}
export async function send<T = unknown>(method: 'GET' | 'POST', path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, { method, headers: { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  const data = text ? JSON.parse(text) : undefined;
  if (!res.ok) throw new ApiError({ ...(data ?? {}), status: res.status });
  return data as T;
}
export const notify = (message: string) => window.dispatchEvent(new CustomEvent('mfe:notify', { detail: { message } }));
"""
STYLES = """/* Sistema de diseño compartido: el shell define los tokens --mfe-* en :root y atraviesan el Shadow DOM.
   Los valores de respaldo permiten ejecutar el remote solo (vite dev). Vocabulario de clases: card, field, campo, hint, btn, alert, table, badge, empty. */
:host{display:block;font-family:var(--mfe-font,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif);color:var(--mfe-text,#1b2430);line-height:1.5}
*{box-sizing:border-box}
.mfe{display:grid;gap:var(--mfe-gap,1.25rem)}
.mfe-title{margin:0;font-size:1.35rem;font-weight:700;letter-spacing:-.01em}
.mfe-sub{margin:.15rem 0 0;color:var(--mfe-muted,#5b6776);font-size:.9rem}
.grid{display:grid;gap:var(--mfe-gap,1.25rem);grid-template-columns:repeat(auto-fill,minmax(min(100%,22rem),1fr));align-items:start}
.card{background:var(--mfe-surface,#fff);border:1px solid var(--mfe-border,#dde3ea);border-radius:var(--mfe-radius,12px);box-shadow:var(--mfe-shadow,0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.08));padding:1.1rem 1.25rem}
.card h3{margin:0 0 .75rem;font-size:1.02rem;font-weight:650}
form{display:grid;gap:.85rem}
.field{display:grid;gap:.3rem;font-size:.9rem;font-weight:600}
.field small{font-weight:400;color:var(--mfe-muted,#5b6776)}
input,select,textarea{font:inherit;color:inherit;width:100%;padding:.55rem .7rem;background:var(--mfe-bg,#f6f8fb);border:1px solid var(--mfe-border,#dde3ea);border-radius:8px;transition:border-color .15s,box-shadow .15s}
input:focus-visible,select:focus-visible,textarea:focus-visible{outline:none;border-color:var(--mfe-primary,#1d4ed8);box-shadow:0 0 0 3px var(--mfe-focus,rgba(29,78,216,.25))}
input[aria-invalid=true],textarea[aria-invalid=true]{border-color:var(--mfe-danger,#b42318)}
.check{display:flex;align-items:center;gap:.5rem;font-weight:500}.check input{width:auto}
.btn,button{font:inherit;font-weight:600;cursor:pointer;padding:.6rem 1rem;border:0;border-radius:8px;background:var(--mfe-primary,#1d4ed8);color:var(--mfe-primary-contrast,#fff);justify-self:start;transition:filter .15s,transform .05s}
.btn:hover,button:hover:not(:disabled){filter:brightness(1.08)}.btn:active,button:active:not(:disabled){transform:translateY(1px)}
button:focus-visible{outline:3px solid var(--mfe-focus,rgba(29,78,216,.45));outline-offset:2px}
button:disabled{opacity:.55;cursor:progress}
.btn-ghost{background:transparent;color:var(--mfe-primary,#1d4ed8);border:1px solid var(--mfe-border,#dde3ea)}
.alert,[role=alert]{margin:0;padding:.6rem .8rem;border-radius:8px;font-size:.9rem;background:var(--mfe-danger-bg,#fdecea);color:var(--mfe-danger,#b42318);border:1px solid var(--mfe-danger,#b42318)}
.ok{padding:.6rem .8rem;border-radius:8px;background:var(--mfe-success-bg,#e7f6ec);color:var(--mfe-success,#05603a)}
.table{width:100%;border-collapse:collapse;font-size:.9rem}.table th,.table td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--mfe-border,#dde3ea)}
.table th{color:var(--mfe-muted,#5b6776);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
.badge{display:inline-block;padding:.1rem .55rem;border-radius:999px;font-size:.75rem;font-weight:650;background:var(--mfe-badge-bg,#e0e9ff);color:var(--mfe-primary,#1d4ed8)}
.empty{padding:1.2rem;text-align:center;color:var(--mfe-muted,#5b6776);border:1px dashed var(--mfe-border,#dde3ea);border-radius:var(--mfe-radius,12px)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.35rem 1rem;margin:0}dt{font-weight:600;color:var(--mfe-muted,#5b6776)}dd{margin:0}
.campo{display:grid;gap:.3rem}
.hint{display:block;margin:0;font-size:.8rem;font-weight:400;line-height:1.35;color:var(--mfe-muted,#5b6776)}
h3 + p.hint{margin:-.4rem 0 .15rem}
"""
SETUP = "import '@testing-library/jest-dom/vitest';\n"


def _form_stub(cm: dict, route: dict | None, prefix: str) -> str:
    name = pascal(cm["command"]) + "Form"
    path = route["path"] if route else ""
    return f"""// FORGE-STUB: formulario genérico. La etapa de microfrontends debe reemplazarlo por campos reales del comando.
import {{ useState, type FormEvent }} from 'react';
import {{ send, notify, ApiError }} from '../api';

/** Comando de usuario: «{cm['command']}» (agregado «{cm['aggregate']}», contexto «{cm['context']}»). Ruta: POST {path} */
export function {name}() {{
  const [id, setId] = useState('');
  const [body, setBody] = useState('{{}}');
  const [error, setError] = useState<string | null>(null);
  async function onSubmit(e: FormEvent) {{
    e.preventDefault();
    setError(null);
    try {{
      await send('POST', `/api/{prefix}{path.removeprefix('/api')}`.replace('{{id}}', id), JSON.parse(body));
      notify('{cm['command']}: listo');
    }} catch (err) {{
      setError(err instanceof ApiError ? (err.problem.regla ?? err.message) : String(err));
    }}
  }}
  return (
    <section className="card">
      <form onSubmit={{onSubmit}} aria-label="{cm['command']}">
        <h3>{cm['command']}</h3>
        <p className="hint">Describe en una línea para qué sirve «{cm['command']}».</p>
        <div className="campo">
          <label className="field">Identificador<input value={{id}} aria-describedby="ayuda-id" onChange={{(e) => setId(e.target.value)}} /></label>
          <small className="hint" id="ayuda-id">Identificador del agregado sobre el que actúa el comando; indica de dónde sale y un ejemplo.</small>
        </div>
        <div className="campo">
          <label className="field">Cuerpo (JSON)<textarea rows={{4}} value={{body}} aria-describedby="ayuda-cuerpo" onChange={{(e) => setBody(e.target.value)}} /></label>
          <small className="hint" id="ayuda-cuerpo">Datos del comando en JSON; reemplázalo por un campo por dato, cada uno con su ayuda.</small>
        </div>
        <button type="submit">{cm['command']}</button>
        {{error && <p role="alert" className="alert">{{error}}</p>}}
      </form>
    </section>
  );
}}
"""


def scaffold_remote(cfg: Config, manifest: dict, r: dict) -> list[str]:
    """Esqueleto del microfrontend (remote) de UN dominio. Los formularios son FORGE-STUB hasta que la etapa de microfrontends los completa."""
    fe = cfg.out / "frontend"
    routes = {}
    for ctx, info in manifest["domains"].items():
        for rt in info["routes"]:
            if rt["command"]:
                routes[rt["command"]] = (rt, kebab(ctx).split("-")[0])
    d = fe / r["slug"]
    (d / "src" / "forms").mkdir(parents=True, exist_ok=True)
    (d / "package.json").write_text(json.dumps({"name": r["slug"], **REMOTE_PKG}, indent=2), encoding="utf-8")
    (d / "vite.config.ts").write_text(VITE_REMOTE.replace("__SLUG__", r["slug"]), encoding="utf-8")
    (d / "tsconfig.json").write_text(TSCONFIG, encoding="utf-8")
    (d / "index.html").write_text(f'<!doctype html><meta charset="utf-8"><title>{r["slug"]}</title>\n<{r["slug"]}></{r["slug"]}>\n'
                                  '<script type="module" src="/src/main.tsx"></script>\n', encoding="utf-8")
    (d / "src" / "main.tsx").write_text(MAIN_TSX.replace("__SLUG__", r["slug"]), encoding="utf-8")
    (d / "src" / "api.ts").write_text(API_TS, encoding="utf-8")
    (d / "src" / "styles.css").write_text(STYLES, encoding="utf-8")
    (d / "src" / "setup-tests.ts").write_text(SETUP, encoding="utf-8")
    (d / "src" / "vite-env.d.ts").write_text('/// <reference types="vite/client" />\n', encoding="utf-8")
    imports, entries = [], []
    for cm in r["commands"]:
        n = pascal(cm["command"]) + "Form"
        route, prefix = routes.get(cm["command"], (None, ""))
        (d / "src" / "forms" / f"{n}.tsx").write_text(_form_stub(cm, route, prefix), encoding="utf-8")
        imports.append(f"import {{ {n} }} from './forms/{n}';")
        entries.append(f"  {{ roles: {json.dumps(cm['roles'], ensure_ascii=False)}, node: <{n} key=\"{n}\" /> }},")
    app = ("\n".join(imports) + "\n\n// FORGE-STUB: la etapa de microfrontends añade aquí la vista de consulta de cada rol.\n"
           "const FORMS: { roles: string[]; node: JSX.Element }[] = [\n" + "\n".join(entries) + "\n];\n\n"
           f"/** `role` llega del shell (atributo data-role); vacío = todos los formularios de «{r['context']}». */\n"
           "export function App({ role }: { role: string }) {\n  return (\n    <main className=\"mfe\">\n"
           f"      <header><h2 className=\"mfe-title\">{r['context']}</h2>{{role && <p className=\"mfe-sub\">{{role}}</p>}}</header>\n"
           "      <div className=\"grid\">{FORMS.filter((f) => !role || f.roles.includes(role)).map((f) => f.node)}</div>\n    </main>\n  );\n}\n")
    (d / "src" / "App.tsx").write_text(app, encoding="utf-8")
    (d / "mfe.json").write_text(json.dumps({"tag": r["slug"], "context": r["context"], "roles": sorted(r["roles"])}, indent=2, ensure_ascii=False), encoding="utf-8")
    return [f"frontend/{r['slug']}"]


SHELL_CSS = """/* Tokens del sistema de diseño: los remotes (Shadow DOM) los heredan como custom properties. */
:root{--mfe-font:Inter,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;--mfe-bg:#f4f6fa;--mfe-surface:#fff;--mfe-text:#1b2430;--mfe-muted:#5b6776;
--mfe-border:#dde3ea;--mfe-primary:#1d4ed8;--mfe-primary-contrast:#fff;--mfe-focus:rgba(29,78,216,.28);--mfe-danger:#b42318;--mfe-danger-bg:#fdecea;
--mfe-success:#05603a;--mfe-success-bg:#e7f6ec;--mfe-badge-bg:#e0e9ff;--mfe-radius:12px;--mfe-gap:1.25rem;--mfe-shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.08);
color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--mfe-bg:#0e1420;--mfe-surface:#161e2e;--mfe-text:#e6ebf2;--mfe-muted:#9aa7b8;--mfe-border:#2a3548;--mfe-primary:#6c9bff;
--mfe-primary-contrast:#0b1220;--mfe-focus:rgba(108,155,255,.35);--mfe-danger:#ff8a80;--mfe-danger-bg:#3a1d1b;--mfe-success:#7ee2a8;--mfe-success-bg:#12301f;--mfe-badge-bg:#1e2f57}}
*{box-sizing:border-box}
body{margin:0;background:var(--mfe-bg);color:var(--mfe-text);font-family:var(--mfe-font);line-height:1.5}
.shell-header{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:center;justify-content:space-between;padding:.75rem clamp(1rem,4vw,2rem);
background:var(--mfe-surface);border-bottom:1px solid var(--mfe-border)}
.brand{display:flex;align-items:center;gap:.6rem;font-weight:700;font-size:1.05rem}.brand i{display:inline-grid;place-items:center;width:2rem;height:2rem;border-radius:9px;background:var(--mfe-primary);color:var(--mfe-primary-contrast);font-style:normal}
.role{display:flex;align-items:center;gap:.6rem;font-size:.85rem;color:var(--mfe-muted)}
.role select{font:inherit;color:var(--mfe-text);background:var(--mfe-bg);border:1px solid var(--mfe-border);border-radius:8px;padding:.45rem .7rem}
.role select:focus-visible{outline:3px solid var(--mfe-focus)}
.shell-main{max-width:76rem;margin:0 auto;padding:clamp(1rem,3vw,2rem);display:grid;gap:2rem}
#toast{position:fixed;right:1rem;bottom:1rem;max-width:min(24rem,calc(100vw - 2rem));padding:.7rem 1rem;border-radius:10px;background:var(--mfe-text);color:var(--mfe-bg);box-shadow:0 8px 24px rgba(0,0,0,.25)}
[hidden]{display:none!important}
"""


def ensure_design_system(cfg: Config, slug: str) -> bool:
    """Migra un remote generado antes del sistema de diseño: si su styles.css no usa los tokens --mfe-*, lo reemplaza por el
    actual. Idempotente: no toca un styles.css que ya los usa (el agente puede haberlo ampliado). Devuelve si cambió algo."""
    css = cfg.out / "frontend" / f"mfe-{slug}" / "src" / "styles.css"
    if not css.parent.exists():
        return False
    if css.exists() and css.read_text(encoding="utf-8", errors="ignore").count("var(--mfe-") >= 10:
        return False
    css.write_text(STYLES, encoding="utf-8")
    return True


SHELL_MAIN = """import './shell.css';

interface Entry { tag: string; module: string; context: string; roles: string[] }
const outlet = document.getElementById('outlet')!;
const select = document.getElementById('role') as HTMLSelectElement;
const toast = document.getElementById('toast')!;

// Composición en tiempo de ejecución: el shell no conoce a los remotes en compilación, solo el manifiesto.
// Cada dominio es dueño de su remote; el rol elegido decide cuáles se muestran y qué formularios ve cada uno.
async function show(manifest: Entry[], role: string) {
  const mine = manifest.filter((m) => m.roles.includes(role));
  for (const m of mine) if (!customElements.get(m.tag)) await import(/* @vite-ignore */ m.module);
  outlet.replaceChildren(...mine.map((m) => Object.assign(document.createElement(m.tag), {}) as HTMLElement).map((el) => {
    el.setAttribute('data-role', role);
    return el;
  }));
}
async function boot() {
  const manifest: Entry[] = await (await fetch('/mfe-manifest.json')).json();
  const roles = [...new Set(manifest.flatMap((m) => m.roles))].sort();
  select.replaceChildren(...roles.map((r) => Object.assign(document.createElement('option'), { value: r, textContent: r })));
  select.addEventListener('change', () => show(manifest, select.value));
  window.addEventListener('mfe:notify', (e) => {
    toast.textContent = (e as CustomEvent).detail.message; toast.hidden = false; setTimeout(() => (toast.hidden = true), 3000);
  });
  if (roles.length) show(manifest, roles[0]);
}
boot();
"""


DOCKERFILE_FRONTEND = """FROM node:22-alpine AS build
WORKDIR /app
COPY . .
RUN for d in mfe-*; do (cd $d && npm install --no-audit --no-fund && npm run build) || exit 1; done
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/mfe-shell/dist /usr/share/nginx/html
{copies}
"""


def scaffold_shell(cfg: Config) -> list[str]:
    """Shell + Dockerfile del gateway; descubre los remotes presentes en out/frontend/*/mfe.json (los que haya construido cualquier equipo)."""
    fe = cfg.out / "frontend"
    metas = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(fe.glob("mfe-*/mfe.json"))]
    sh = fe / "mfe-shell"
    (sh / "src").mkdir(parents=True, exist_ok=True)
    (sh / "public").mkdir(exist_ok=True)
    (sh / "package.json").write_text(json.dumps({"name": "mfe-shell", "private": True, "type": "module",
                                                 "scripts": {"dev": "vite", "build": "tsc --noEmit && vite build"},
                                                 "devDependencies": {"typescript": "^5.5.4", "vite": "^5.4.2"}}, indent=2), encoding="utf-8")
    (sh / "tsconfig.json").write_text(json.dumps({"compilerOptions": {"target": "ES2020", "lib": ["ES2020", "DOM"], "module": "ESNext",
                                                                      "moduleResolution": "bundler", "strict": True, "skipLibCheck": True,
                                                                      "noEmit": True}, "include": ["src"]}, indent=2), encoding="utf-8")
    (sh / "index.html").write_text('<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                                   '<title>Mantenimiento preventivo de drones</title></head>\n'
                                   '<body><header class="shell-header"><div class="brand"><i aria-hidden="true">✈</i>AgroDrones · Mantenimiento</div>'
                                   '<label class="role">Rol <select id="role"></select></label></header>\n'
                                   '<main class="shell-main" id="outlet"></main><div id="toast" role="status" hidden></div>\n'
                                   '<script type="module" src="/src/main.ts"></script></body></html>\n', encoding="utf-8")
    (sh / "src" / "shell.css").write_text(SHELL_CSS, encoding="utf-8")
    (sh / "src" / "main.ts").write_text(SHELL_MAIN, encoding="utf-8")
    (sh / "public" / "mfe-manifest.json").write_text(json.dumps(
        [{"tag": m["tag"], "context": m["context"], "roles": m["roles"], "module": f"/mfe/{m['tag']}/{m['tag']}.js"} for m in metas],
        indent=2, ensure_ascii=False), encoding="utf-8")
    if gateway(cfg, True) == "nginx":
        copies = "\n".join(f"COPY --from=build /app/{m['tag']}/dist /usr/share/nginx/html/mfe/{m['tag']}" for m in metas)
        (fe / "Dockerfile").write_text(DOCKERFILE_FRONTEND.format(copies=copies), encoding="utf-8")
    (fe / ".dockerignore").write_text("**/node_modules\n**/dist\n",
                                      encoding="utf-8")
    if gateway(cfg, True) == "nginx":
        (fe / "nginx.conf").write_text(_nginx(cfg), encoding="utf-8")
    (fe / "README.md").write_text("# Microfrontends\n\nShell + un remote por **dominio** (Web Components); el shell filtra por rol. "
                                  "Cada remote lo construye el equipo dueño del dominio.\n", encoding="utf-8")
    return ["frontend/mfe-shell", "frontend/.dockerignore"] + (["frontend/Dockerfile", "frontend/nginx.conf"] if gateway(cfg, True) == "nginx" else [])


# ----------------------------------------------------------------------------- instrucciones de proyecto
SERVICE_AGENTS_MD = """# Servicio «{context}» ({language} · {architecture} · {style} · {database})

Generado a partir del modelo ArchiMate según las decisiones del arquitecto
(`docs/{slug}/decisiones.toml`). Patrones elegidos: {patterns}.

- Contratos de integración: ver el contrato del bus del ensamblado (`docs/contrato-bus.md`) y `docs/{slug}/`.
- Nombres de dominio en español, sin tildes, como el modelo. SOLID, DDD, dependencias hacia adentro.
- Todo cambio de comportamiento lleva prueba; las pruebas son herméticas (sin red ni Docker).
- No hagas `git commit`: el orquestador versiona por etapa.
"""


def platform(cfg: Config, ir: dict, manifest: dict, target: Path, services_rel: str, with_frontend: bool) -> list[str]:
    """Plataforma común generada del ArchiMate: bus, simuladores, compose y contrato. cfg.domains = los dominios REALES de este ensamblado;
    todo lo demás se simula. Es determinista: dos personas con los mismos dominios obtienen exactamente lo mismo."""
    target.mkdir(parents=True, exist_ok=True)
    bt = bus_topics(ir, cfg, manifest)
    files: dict[str, str] = {}
    files["docs/contrato-bus.md"] = contract_doc(ir, cfg, manifest, bt)
    files["event-bus/bus.py"] = BUS_PY
    files["event-bus/topics.json"] = json.dumps(bt, indent=2, ensure_ascii=False)
    if mensajeria(cfg, bt) == "rabbitmq":
        files["event-bus/Dockerfile"] = BUS_DOCKER
        files["event-bus/requirements.txt"] = "pika==1.3.2\n"
        files["event-bus/README.md"] = BUS_README
    else:
        files["event-bus/Dockerfile"] = PY_DOCKER.format(script="bus.py")
        files["event-bus/README.md"] = BUS_README_MEMORIA
    emits, apis = [], []
    for s in manifest["simulated"]:
        for ev in s["emits"]:
            t = next((x for x in bt["topics"] if x["event"] == ev and x["publisher"] == s["context"]), None)
            if t:
                emits.append({"context": s["context"], "context_slug": kebab(s["context"]), "event": ev, "event_slug": kebab(ev),
                              "topic": t["topic"], "sample": t["sample"]})
    for ctx_name, info in manifest["domains"].items():
        for ac in info["acl"]:
            if ac.get("upstream_real"):
                continue          # el proveedor es un servicio real: no se simula
            e = {"context": ac["upstream"], "context_slug": kebab(ac["upstream"]), "operation": ac["name"], "operation_slug": ac["slug"]}
            if e not in apis:
                apis.append(e)
    files["simulators/simulators.py"] = SIM_PY
    files["simulators/simulators.json"] = json.dumps({"emits": emits, "apis": apis}, indent=2, ensure_ascii=False)
    files["simulators/Dockerfile"] = PY_DOCKER.format(script="simulators.py")
    files["simulators/README.md"] = ("# Simuladores de los contextos no implementados\n\n" +
                                     "\n".join(f"- **{s['context']}**: emite {s['emits'] or '—'}, se suscribe a {s['subscribes'] or '—'}, APIs {s['sync_apis'] or '—'}" for s in manifest["simulated"]) + "\n")
    compose, sql = _compose(cfg, bt, services_rel, with_frontend, ir)
    files["docker-compose.yml"], files["init-postgres.sql"] = compose, sql
    if gateway(cfg, with_frontend) == "propio":
        files["docs/gateway-rutas.md"] = gateway_doc(cfg)
    else:
        files["nginx.conf"] = _nginx(cfg)
    for rel, text in files.items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return list(files)


def smoke_dir(cfg: Config, d) -> Path:
    return cfg.out / ".platform" / d.slug


def modulo_durable(d) -> str:
    """Ruta de import (relativa al paquete) del módulo durable: respeta la arquitectura decidida."""
    return "infrastructure.mensajeria" if d.architecture == "clean-ddd" else "adapters.outbound.mensajeria"


def durable_files(cfg: Config, d) -> dict[str, str]:
    """Esqueletos deterministas de outbox/inbox durable (python + outbox): ruta relativa al servicio -> contenido.

    El módulo y sus pruebas canónicas son la fuente de verdad del patrón: los agentes los cablean,
    no los reimplementan. La puerta `outbox_gate` restaura y ejecuta las pruebas canónicas.
    """
    if d.language != "python" or not d.uses("outbox"):
        return {}
    paquete = d.slug.replace("-", "_")
    modulo = modulo_durable(d)
    archivos = {
        f"src/{paquete}/__init__.py": "",
        f"src/{paquete}/{modulo.replace('.', '/')}.py": (SKELETONS / "mensajeria.py.tmpl").read_text(encoding="utf-8"),
        "tests/test_mensajeria_durable.py": (SKELETONS / "test_mensajeria.py.tmpl").read_text(encoding="utf-8")
        .replace("__PAQUETE__", paquete).replace("__MODULO__", modulo),
    }
    acumulado = f"src/{paquete}"
    for parte in modulo.split(".")[:-1]:
        acumulado += f"/{parte}"
        archivos.setdefault(f"{acumulado}/__init__.py", "")
    return archivos


def domain_scaffold(cfg: Config, ir: dict, manifest: dict) -> list[str]:
    """S02 (determinista) para UN dominio: metadatos, copia de sus decisiones, esqueleto del microfrontend y plataforma de humo aislada."""
    import shutil
    d = cfg.domains[0]
    out = cfg.out
    svc = out / d.dir
    svc.mkdir(parents=True, exist_ok=True)
    (out / "docs" / d.slug).mkdir(parents=True, exist_ok=True)
    (svc / "forge-domain.json").write_text(json.dumps(
        {"context": d.context, "language": d.language, "architecture": d.architecture, "style": d.style, "database": d.database,
         "port": d.port, "patterns": sorted(p for p in d.patterns if d.uses(p))}, indent=2, ensure_ascii=False), encoding="utf-8")
    src = cfg.decisions_dir / f"{d.slug}.toml"
    if src.exists():
        shutil.copy(src, out / "docs" / d.slug / "decisiones.toml")
    (svc / "AGENTS.md").write_text(SERVICE_AGENTS_MD.format(context=d.context, language=d.language, architecture=d.architecture, style=d.style,
                                                            database=d.database, slug=d.slug, patterns=", ".join(sorted(p for p in d.patterns if d.uses(p))) or "ninguno"), encoding="utf-8")
    (svc / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    (out / ".gitignore").write_text("bin/\nobj/\nnode_modules/\ndist/\n.venv/\n__pycache__/\n*.pyc\n.pytest_cache/\nTestResults/\ntarget/\n.env\n.platform/\n", encoding="utf-8")
    (out / "docs" / d.slug / "supuestos.md").write_text(f"# Supuestos de diseño — {d.context}\n\n- Los campos de los eventos entre contextos son supuestos (ver `contrato-bus.md`): el modelo ArchiMate no los define.\n", encoding="utf-8")
    created = []
    for rel, contenido in durable_files(cfg, d).items():
        destino = svc / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith("__init__.py") and destino.exists():
            continue
        destino.write_text(contenido, encoding="utf-8")
        created.append(f"{d.dir}/{rel}")
    for r in manifest["frontend"]["remotes"]:
        created += scaffold_remote(cfg, manifest, r)
    created += platform(cfg, ir, manifest, smoke_dir(cfg, d), "../../services", with_frontend=False)
    return created + [d.dir + "/forge-domain.json"]


def assemble_files(cfg: Config, ir: dict, manifest: dict) -> list[str]:
    """Ensamblado (forge assemble): plataforma completa en out/ con TODOS los dominios presentes + shell de microfrontends."""
    created = platform(cfg, ir, manifest, cfg.out, "./services", with_frontend=True)
    created += scaffold_shell(cfg)
    (cfg.out / "AGENTS.md").write_text("# Producto generado por ArchiForge\n\nServicios en `services/`, microfrontends en `frontend/`, "
                                       "decisiones y verificación por dominio en `docs/<dominio>/`. Contrato común: `docs/contrato-bus.md`.\n", encoding="utf-8")
    (cfg.out / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    return created
