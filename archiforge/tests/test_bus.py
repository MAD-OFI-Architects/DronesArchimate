"""El bus por tópicos: topología de colas, política de reintentos y despliegue sobre RabbitMQ (sin broker real)."""
import dataclasses
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forge import config, decisions, scaffold  # noqa: E402
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


BASE = {"mensajeria": "rabbitmq", "gateway": "nginx", "frontend": "microfrontends", "despliegue": "docker-compose", "simuladores": "generar"}


def _plataforma(**cambios):
    decisiones = {**BASE, **cambios}
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), platform={k: v for k, v in decisiones.items() if v})
    ir = build_ir(cfg.archimate, cfg.docs_dir)
    manifest = build_manifest(ir, cfg.domains, cfg.con_frontend)
    return cfg, ir, manifest, scaffold.bus_topics(ir, cfg, manifest, decisiones.get("simuladores") != "ninguno")


def _compose(**cambios):
    cfg, ir, _, bt = _plataforma(**cambios)
    return scaffold._compose(cfg, bt, "./services", True, ir)[0]


def _exigida(clave, destino, **cambios):
    cfg, ir, manifest, bt = _plataforma(**{clave: None}, **cambios)
    try:
        scaffold.platform(cfg, ir, manifest, destino, "./services", True)
    except SystemExit as e:
        return str(e)
    raise AssertionError(f"debía exigir la decisión «{clave}»")


def test_con_rabbitmq_el_compose_lo_incluye_y_el_bus_espera_al_broker():
    c = _compose()
    assert "  rabbitmq:\n    image: rabbitmq:3.13-management-alpine" in c and "RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/" in c
    assert "rabbitmq:\n        condition: service_healthy" in c


def test_con_memoria_no_hay_broker_en_el_compose_ni_dependencias_en_el_bus(tmp_path):
    cfg, ir, manifest, bt = _plataforma(mensajeria="memoria")
    compose, _ = scaffold._compose(cfg, bt, "./services", True, ir)
    assert "rabbitmq" not in compose and "RABBITMQ_URL" not in compose
    archivos = scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    assert "event-bus/requirements.txt" not in archivos and "pip install" not in (tmp_path / "plat/event-bus/Dockerfile").read_text()
    assert "no conserva los mensajes" in (tmp_path / "plat/docs/contrato-bus.md").read_text(encoding="utf-8")


def test_la_herramienta_no_elige_por_el_arquitecto_ninguna_decision_de_plataforma(tmp_path):
    for clave, texto, flag in (("mensajeria", "el canal de eventos", "--messaging"), ("gateway", "el gateway", "--gateway"),
                               ("frontend", "el frontend", "--frontend"), ("despliegue", "el despliegue", "--deployment"),
                               ("simuladores", "los simuladores", "--simulators")):
        mensaje = _exigida(clave, tmp_path / clave)
        assert f"Falta decidir {texto}" in mensaje and flag in mensaje, clave
        assert all(o in mensaje for o in decisions.ELECCIONES_DE_PLATAFORMA[clave][1])          # lista todas las opciones, sin recomendar


def test_la_decision_de_plataforma_se_escribe_y_se_lee(tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), decisions_dir=tmp_path)
    decisions.write_platform(cfg, {"mensajeria": "rabbitmq", "gateway": "propio"}, {"mensajeria": "durabilidad"}, {"mongo": "mongo:8"})
    leido = decisions.read_platform(cfg)
    assert (leido["mensajeria"], leido["gateway"], leido["imagenes"]) == ("rabbitmq", "propio", {"mongo": "mongo:8"})
    assert leido["justificacion"] == {"mensajeria": "durabilidad"}
    decisions.write_platform(cfg, {"gateway": "nginx"})                          # lo que no se pasa conserva su valor
    leido = decisions.read_platform(cfg)
    assert leido["mensajeria"] == "rabbitmq" and leido["gateway"] == "nginx" and leido["imagenes"] == {"mongo": "mongo:8"}
    assert decisions.load_all(cfg) == []                                          # plataforma.toml no es un dominio


def test_una_opcion_o_imagen_inexistente_se_rechaza(tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), decisions_dir=tmp_path)
    for malo in ({"gateway": "kong"}, {"frontend": "angular"}, {"despliegue": "kubernetes"}, {"inventada": "x"}):
        try:
            decisions.write_platform(cfg, malo)
        except SystemExit:
            continue
        raise AssertionError(f"debía rechazar {malo}")
    try:
        decisions.write_platform(cfg, imagenes={"redis": "redis:7"})
    except SystemExit as e:
        assert "desconocida" in str(e)
    else:
        raise AssertionError("debía rechazar la imagen")


def test_con_gateway_propio_no_hay_nginx_y_cada_servicio_publica_su_puerto(tmp_path):
    cfg, ir, manifest, bt = _plataforma(gateway="propio")
    compose = scaffold._compose(cfg, bt, "./services", True, ir)[0]
    assert "  gateway:" not in compose and "nginx" not in compose
    for d in cfg.domains:
        assert f'      - "{d.port}:{d.port}"' in compose
    archivos = scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    assert "nginx.conf" not in archivos and "docs/gateway-rutas.md" in archivos
    rutas = (tmp_path / "plat/docs/gateway-rutas.md").read_text(encoding="utf-8")
    assert "/api/intervenciones/…" in rutas and "/mfe/<etiqueta>/<etiqueta>.js" in rutas


def test_con_nginx_se_genera_el_gateway_y_el_humo_por_dominio_es_interno():
    assert "  gateway:\n    build: ./frontend" in _compose()
    cfg, ir, _, bt = _plataforma(gateway=None, frontend=None, despliegue=None, simuladores=None)
    humo = scaffold._compose(cfg, bt, "./services", False, ir)[0]                  # sin decisiones: el humo no las necesita
    assert "  gateway:\n    image: nginx" in humo and "  simulators:" in humo


def test_sin_frontend_no_hay_remotes_ni_shell_y_el_gateway_solo_enruta(tmp_path):
    cfg, ir, manifest, bt = _plataforma(frontend="ninguno")
    assert manifest["frontend"]["remotes"] == [] and not [i for i in manifest["items"] if i["kind"] == "form"]
    compose = scaffold._compose(cfg, bt, "./services", True, ir)[0]
    assert "build: ./frontend" not in compose and "  gateway:\n    image: nginx" in compose
    scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    nginx = (tmp_path / "plat/nginx.conf").read_text(encoding="utf-8")
    assert "/api/intervenciones/" in nginx and "/mfe/" not in nginx and "try_files" not in nginx
    assert scaffold.scaffold_shell.__name__ and not cfg.con_frontend


def test_sin_despliegue_generado_no_hay_compose_ni_sql(tmp_path):
    cfg, ir, manifest, _ = _plataforma(despliegue="propio")
    archivos = scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    assert "docker-compose.yml" not in archivos and "init-postgres.sql" not in archivos and "event-bus/bus.py" in archivos


def test_sin_simuladores_no_hay_contenedor_ni_ruta_ni_suscriptores_simulados_y_las_url_las_pone_el_equipo(tmp_path):
    cfg, ir, manifest, bt = _plataforma(simuladores="ninguno")
    compose = scaffold._compose(cfg, bt, "./services", True, ir)[0]
    assert "  simulators:" not in compose and "http://simulators" not in compose
    assert 'HABILITACION_DE_PERSONAL_API_URL: "${HABILITACION_DE_PERSONAL_API_URL:-}"' in compose.replace("\\", "")
    assert all("simulators" not in sub["url"] for t in bt["topics"] for sub in t["subscribers"])
    archivos = scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    assert not [a for a in archivos if a.startswith("simulators/")] and "/sim/" not in (tmp_path / "plat/nginx.conf").read_text(encoding="utf-8")


def test_las_versiones_de_imagen_son_las_que_el_arquitecto_fijo(tmp_path):
    cfg, ir, manifest, bt = _plataforma()
    cfg = dataclasses.replace(cfg, platform={**cfg.platform, "imagenes": {"mongo": "mongo:8", "postgres": "postgres:17", "python": "python:3.13-slim"}})
    compose = scaffold._compose(cfg, bt, "./services", True, ir)[0]
    assert "image: mongo:8" in compose and "image: postgres:17" in compose and "image: mongo:7" not in compose
    assert "image: rabbitmq:3.13-management-alpine" in compose                      # lo no fijado conserva la versión de la herramienta
    scaffold.platform(cfg, ir, manifest, tmp_path / "plat", "./services", True)
    assert (tmp_path / "plat/event-bus/Dockerfile").read_text().startswith("FROM python:3.13-slim")
