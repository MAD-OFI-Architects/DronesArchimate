"""Bus de eventos por tópicos. Con RABBITMQ_URL los mensajes viven en RabbitMQ (colas durables, reintentos con espera y
cola de mensajes muertos por suscriptor); sin ella, un modo en memoria solo para pruebas herméticas.

El contrato HTTP no cambia: los servicios publican con `POST /publish` y reciben con `POST /events/{topic}`.
Por cada (tópico, suscriptor) hay una cola `<tópico>::<contexto>`, una cola de espera `.retry` (el mensaje vuelve a la
cola principal tras BUS_ESPERA_MS) y una `.dlq` donde queda el mensaje tras BUS_MAX_INTENTOS entregas fallidas.
Un único consumidor por cola mantiene el orden de entrega al suscriptor mientras no hay fallos."""
import json, os, re, threading, time, unicodedata, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CFG = json.load(open(os.environ.get("TOPICS_FILE", "topics.json"), encoding="utf-8"))
RABBIT = os.environ.get("RABBITMQ_URL", "")
MAX_INTENTOS = int(os.environ.get("BUS_MAX_INTENTOS", "5"))
ESPERA_MS = int(os.environ.get("BUS_ESPERA_MS", "5000"))
EXCHANGE = "eventos"
LOG, LOCK, LISTO = [], threading.Lock(), threading.Event()


def slug(texto):
    ascii_ = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")


def plan_de_colas(cfg):
    """Una entrada por (tópico, suscriptor): la cola principal, la de espera y la de mensajes muertos."""
    return [{"topic": t["topic"], "contexto": s["context"], "url": s["url"],
             "cola": f"{t['topic']}::{slug(s['context'])}", "reintento": f"{t['topic']}::{slug(s['context'])}.retry",
             "dlq": f"{t['topic']}::{slug(s['context'])}.dlq"} for t in cfg["topics"] for s in t["subscribers"]]


def siguiente_paso(intentos, maximo=None):
    """Tras `intentos` entregas fallidas: reintentar tras la espera, o dejar el mensaje en la cola de mensajes muertos."""
    return "reintentar" if intentos < (maximo or MAX_INTENTOS) else "dead-letter"


def entregar(url, envelope, timeout=5):
    try:
        req = urllib.request.Request(url, json.dumps(envelope).encode(), {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return (200 <= r.status < 300), f"HTTP {r.status}"
    except Exception as e:  # noqa: BLE001 — cualquier fallo de entrega cuenta como intento fallido
        return False, f"{type(e).__name__}: {e}"


# ------------------------------------------------------------------ RabbitMQ
def conectar():
    import pika
    return pika.BlockingConnection(pika.URLParameters(RABBIT))


def declarar(canal):
    canal.exchange_declare(EXCHANGE, "topic", durable=True)
    for c in plan_de_colas(CFG):
        canal.queue_declare(c["cola"], durable=True)
        canal.queue_bind(c["cola"], EXCHANGE, c["topic"])
        canal.queue_declare(c["reintento"], durable=True, arguments={
            "x-message-ttl": ESPERA_MS, "x-dead-letter-exchange": "", "x-dead-letter-routing-key": c["cola"]})
        canal.queue_declare(c["dlq"], durable=True)


def _propiedades(message_id, headers=None):
    import pika
    return pika.BasicProperties(content_type="application/json", delivery_mode=2, message_id=message_id, headers=headers)


class Publicador:
    def __init__(self):
        self._lock, self._con, self._canal = threading.Lock(), None, None

    def _cerrar(self):
        try:
            if self._con is not None and self._con.is_open:
                self._con.close()
        except Exception:  # noqa: BLE001
            pass
        self._con = self._canal = None

    def publicar(self, topic, envelope):
        cuerpo = json.dumps(envelope).encode()
        with self._lock:
            for intento in (1, 2):
                try:
                    if self._canal is None or self._con.is_closed:
                        self._con = conectar(); self._canal = self._con.channel(); self._canal.confirm_delivery()
                    self._canal.basic_publish(EXCHANGE, topic, cuerpo, _propiedades(str(envelope["eventId"])))
                    return
                except Exception:  # noqa: BLE001 — conexión caída: se reabre una vez
                    self._cerrar()
                    if intento == 2:
                        raise


def al_recibir(canal, metodo, props, cuerpo, item):
    ok, error = entregar(item["url"], json.loads(cuerpo))
    if ok:
        return canal.basic_ack(metodo.delivery_tag)
    intentos = int((props.headers or {}).get("x-intentos", 0)) + 1
    destino = item["reintento"] if siguiente_paso(intentos) == "reintentar" else item["dlq"]
    try:
        canal.basic_publish("", destino, cuerpo, _propiedades(props.message_id, {"x-intentos": intentos, "x-error": error[:200]}))
        canal.basic_ack(metodo.delivery_tag)
    except Exception:  # noqa: BLE001 — si no se pudo reubicar, el mensaje vuelve a la cola
        canal.basic_nack(metodo.delivery_tag, requeue=True)


def consumir(item):
    while True:
        try:
            con = conectar(); canal = con.channel(); canal.confirm_delivery(); canal.basic_qos(prefetch_count=1)
            canal.basic_consume(item["cola"], lambda c, m, p, b: al_recibir(c, m, p, b, item))
            canal.start_consuming()
        except Exception:  # noqa: BLE001 — el broker se reinició o aún no está: se reintenta
            time.sleep(2)


def arrancar_rabbit():
    while True:
        try:
            con = conectar(); declarar(con.channel()); con.close(); break
        except Exception:  # noqa: BLE001
            time.sleep(2)
    for item in plan_de_colas(CFG):
        threading.Thread(target=consumir, args=(item,), daemon=True).start()
    LISTO.set()


def mensajes_muertos():
    con = conectar(); canal = con.channel()
    try:
        return {c["dlq"]: canal.queue_declare(c["dlq"], passive=True).method.message_count for c in plan_de_colas(CFG)}
    finally:
        con.close()


def reprocesar_muertos():
    """Devuelve a su cola principal los mensajes de las colas de mensajes muertos (reinicia sus intentos)."""
    con = conectar(); canal = con.channel(); canal.confirm_delivery(); movidos = {}
    try:
        for c in plan_de_colas(CFG):
            n = 0
            while True:
                metodo, props, cuerpo = canal.basic_get(c["dlq"], auto_ack=False)
                if metodo is None:
                    break
                canal.basic_publish("", c["cola"], cuerpo, _propiedades(props.message_id))
                canal.basic_ack(metodo.delivery_tag); n += 1
            movidos[c["dlq"]] = n
        return movidos
    finally:
        con.close()


# ------------------------------------------------------------------ modo memoria (solo pruebas)
def entregar_con_reintentos(url, envelope, attempts=5):
    for i in range(attempts):
        if entregar(url, envelope)[0]:
            return True
        time.sleep(min(2 ** i * 0.3, 5))
    return False


PUBLICADOR = Publicador() if RABBIT else None


class H(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200 if (LISTO.is_set() or not RABBIT) else 503, {"status": "ok" if (LISTO.is_set() or not RABBIT) else "iniciando", "broker": "rabbitmq" if RABBIT else "memoria"})
        if self.path == "/events":
            with LOCK:
                return self._send(200, LOG[-200:])
        if self.path == "/topics":
            return self._send(200, CFG)
        if self.path == "/dlq" and RABBIT:
            try:
                return self._send(200, mensajes_muertos())
            except Exception as e:  # noqa: BLE001
                return self._send(503, {"error": f"broker no disponible: {e}"})
        self._send(404, {"error": "no existe"})

    def do_POST(self):
        if self.path == "/dlq/reprocesar" and RABBIT:
            try:
                return self._send(200, reprocesar_muertos())
            except Exception as e:  # noqa: BLE001
                return self._send(503, {"error": f"broker no disponible: {e}"})
        if self.path != "/publish":
            return self._send(404, {"error": "no existe"})
        try:
            env = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            topic = env["topic"]; env["eventId"]
        except Exception:
            return self._send(400, {"error": "sobre inválido: se requieren topic y eventId"})
        subs = [c for c in plan_de_colas(CFG) if c["topic"] == topic]
        entry = {"topic": topic, "eventId": env["eventId"], "subscribers": [c["url"] for c in subs], "delivered": {}}
        with LOCK:
            LOG.append(entry)
        if RABBIT:
            try:
                PUBLICADOR.publicar(topic, env)
            except Exception as e:  # noqa: BLE001 — el servicio emisor reintenta desde su bandeja de salida
                return self._send(503, {"error": f"broker no disponible: {e}"})
        else:
            for c in subs:
                threading.Thread(target=lambda c=c: entry["delivered"].__setitem__(c["url"], entregar_con_reintentos(c["url"], env)), daemon=True).start()
        self._send(202, {"accepted": True, "subscribers": len(subs)})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if RABBIT:
        threading.Thread(target=arrancar_rabbit, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "5100"))), H).serve_forever()
