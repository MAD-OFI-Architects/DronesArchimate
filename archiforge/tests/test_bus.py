"""El bus por tópicos: topología de colas, política de reintentos y despliegue sobre RabbitMQ (sin broker real)."""
import dataclasses
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forge import config, scaffold  # noqa: E402
from forge.archimate import build_ir  # noqa: E402
from forge.manifest import build_manifest  # noqa: E402

TOPICS = {"topics": [
    {"topic": "plan.parada.v1", "subscribers": [{"context": "Intervenciones", "url": "http://i/events/x"},
                                                  {"context": "Repuestos del Taller", "url": "http://r/events/x"}]},
    {"topic": "intervenciones.cerrada.v1", "subscribers": [{"context": "Repuestos del Taller", "url": "http://r/events/y"}]}]}


def cargar_bus(tmp_path, monkeypatch, **env):
    (tmp_path / "topics.json").write_text(json.dumps(TOPICS), encoding="utf-8")
    monkeypatch.setenv("TOPICS_FILE", str(tmp_path / "topics.json"))
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    modulo = types.ModuleType("bus_bajo_prueba")
    exec(compile((scaffold.SKELETONS / "bus.py.tmpl").read_text(encoding="utf-8"), "bus.py", "exec"), modulo.__dict__)
    return modulo


def test_hay_una_cola_principal_de_espera_y_de_mensajes_muertos_por_suscriptor(tmp_path, monkeypatch):
    bus = cargar_bus(tmp_path, monkeypatch)
    plan = bus.plan_de_colas(bus.CFG)
    assert len(plan) == 3                                                        # (tópico, suscriptor): 2 + 1
    primero = plan[0]
    assert primero["cola"] == "plan.parada.v1::intervenciones"
    assert primero["reintento"] == primero["cola"] + ".retry" and primero["dlq"] == primero["cola"] + ".dlq"
    assert plan[1]["cola"] == "plan.parada.v1::repuestos-del-taller"            # sin tildes ni espacios


def test_tras_agotar_los_intentos_el_mensaje_va_a_la_cola_de_mensajes_muertos(tmp_path, monkeypatch):
    bus = cargar_bus(tmp_path, monkeypatch, BUS_MAX_INTENTOS="3")
    assert [bus.siguiente_paso(n) for n in (1, 2, 3)] == ["reintentar", "reintentar", "dead-letter"]


def test_la_entrega_falla_con_un_mensaje_si_el_suscriptor_no_responde(tmp_path, monkeypatch):
    bus = cargar_bus(tmp_path, monkeypatch)
    ok, error = bus.entregar("http://127.0.0.1:9/events/x", {"eventId": "e"}, timeout=1)
    assert ok is False and error


def test_sin_broker_el_bus_trabaja_en_memoria_y_lo_dice(tmp_path, monkeypatch):
    bus = cargar_bus(tmp_path, monkeypatch)
    assert bus.RABBIT == "" and bus.PUBLICADOR is None


def _plataforma(tmp_path, mensajeria, gateway="nginx"):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), platform={"mensajeria": mensajeria, "gateway": gateway} if mensajeria or gateway else {})
    ir = build_ir(cfg.archimate, cfg.docs_dir)
    manifest = build_manifest(ir, cfg.domains)
    return cfg, ir, manifest, scaffold.bus_topics(ir, cfg, manifest)


def test_con_rabbitmq_el_compose_lo_incluye_y_el_bus_espera_al_broker(tmp_path):
    cfg, ir, _, bt = _plataforma(tmp_path, "rabbitmq")
    compose, _ = scaffold._compose(cfg, bt, "./services", True, ir)
    assert "  rabbitmq:\n    image: rabbitmq:3.13-management-alpine" in compose
    assert "RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/" in compose
    assert "rabbitmq:\n        condition: service_healthy" in compose


def test_con_memoria_no_hay_broker_en_el_compose_ni_dependencias_en_el_bus(tmp_path):
    cfg, ir, manifest, bt = _plataforma(tmp_path, "memoria")
    compose, _ = scaffold._compose(cfg, bt, "./services", True, ir)
    assert "rabbitmq" not in compose and "RABBITMQ_URL" not in compose
    destino = tmp_path / "plat"
    archivos = scaffold.platform(cfg, ir, manifest, destino, "./services", True)
    assert "event-bus/requirements.txt" not in archivos and "pip install" not in (destino / "event-bus/Dockerfile").read_text()
    assert "no conserva los mensajes" in (destino / "docs/contrato-bus.md").read_text(encoding="utf-8")


def test_sin_decision_la_herramienta_no_elige_el_canal_de_eventos(tmp_path):
    cfg, ir, manifest, bt = _plataforma(tmp_path, None)
    try:
        scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    except SystemExit as e:
        assert "Falta decidir el canal de eventos" in str(e) and "rabbitmq" in str(e) and "memoria" in str(e)
    else:
        raise AssertionError("debía exigir la decisión")


def test_la_decision_de_plataforma_se_escribe_y_se_lee(tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), decisions_dir=tmp_path)
    from forge import decisions
    decisions.write_platform(cfg, "rabbitmq", "propio", {"mensajeria": "durabilidad"})
    assert decisions.read_platform(cfg) == {"mensajeria": "rabbitmq", "gateway": "propio", "justificacion": {"mensajeria": "durabilidad"}}
    decisions.write_platform(cfg, gateway="nginx")                               # lo que no se pasa conserva su valor
    assert decisions.read_platform(cfg)["mensajeria"] == "rabbitmq" and decisions.read_platform(cfg)["gateway"] == "nginx"
    assert decisions.load_all(cfg) == []                                          # plataforma.toml no es un dominio


def test_con_gateway_propio_no_hay_nginx_y_cada_servicio_publica_su_puerto(tmp_path):
    cfg, ir, manifest, bt = _plataforma(tmp_path, "rabbitmq", "propio")
    compose, _ = scaffold._compose(cfg, bt, "./services", True, ir)
    assert "  gateway:" not in compose and "nginx" not in compose
    for d in cfg.domains:
        assert f'      - "{d.port}:{d.port}"' in compose
    destino = tmp_path / "plat"
    archivos = scaffold.platform(cfg, ir, manifest, destino, "./services", True)
    assert "nginx.conf" not in archivos and "docs/gateway-rutas.md" in archivos
    rutas = (destino / "docs/gateway-rutas.md").read_text(encoding="utf-8")
    assert "/api/intervenciones/…" in rutas and "/mfe/<etiqueta>/<etiqueta>.js" in rutas


def test_con_nginx_se_genera_el_gateway_y_sin_decision_no_se_elige(tmp_path):
    cfg, ir, manifest, bt = _plataforma(tmp_path, "rabbitmq", "nginx")
    assert "  gateway:\n    build: ./frontend" in scaffold._compose(cfg, bt, "./services", True, ir)[0]
    cfg, ir, manifest, bt = _plataforma(tmp_path, "rabbitmq", None)
    cfg = dataclasses.replace(cfg, platform={"mensajeria": "rabbitmq"})
    try:
        scaffold._compose(cfg, bt, "./services", True, ir)
    except SystemExit as e:
        assert "Falta decidir el gateway" in str(e) and "nginx" in str(e) and "propio" in str(e)
    else:
        raise AssertionError("debía exigir la decisión")
    assert "  gateway:\n    image: nginx" in scaffold._compose(cfg, bt, "./services", False, ir)[0]     # el humo por dominio es interno
