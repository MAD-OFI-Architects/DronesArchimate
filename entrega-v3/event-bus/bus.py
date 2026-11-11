"""Bus de eventos por tópicos (hace el papel de RabbitMQ / Azure Service Bus). Solo biblioteca estándar."""
import json, os, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CFG = json.load(open(os.environ.get("TOPICS_FILE", "topics.json"), encoding="utf-8"))
SUBS = {t["topic"]: [s["url"] for s in t["subscribers"]] for t in CFG["topics"]}
LOG, LOCK = [], threading.Lock()


def deliver(url, envelope, attempts=5):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, json.dumps(envelope).encode(), {"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=5) as r:
                if 200 <= r.status < 300:
                    return True
        except Exception:
            pass
        time.sleep(min(2 ** i * 0.3, 5))
    return False


class H(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        if self.path == "/events":
            with LOCK:
                return self._send(200, LOG[-200:])
        if self.path == "/topics":
            return self._send(200, CFG)
        self._send(404, {"error": "no existe"})

    def do_POST(self):
        if self.path != "/publish":
            return self._send(404, {"error": "no existe"})
        try:
            env = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            topic = env["topic"]; env["eventId"]
        except Exception:
            return self._send(400, {"error": "sobre inválido: se requieren topic y eventId"})
        urls = SUBS.get(topic, [])
        entry = {"topic": topic, "eventId": env["eventId"], "subscribers": urls, "delivered": {}}
        with LOCK:
            LOG.append(entry)
        for u in urls:
            threading.Thread(target=lambda u=u: entry["delivered"].__setitem__(u, deliver(u, env)), daemon=True).start()
        self._send(202, {"accepted": True, "subscribers": len(urls)})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "5100"))), H).serve_forever()
