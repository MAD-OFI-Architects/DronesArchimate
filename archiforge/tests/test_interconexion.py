"""Fase 1: las APIs síncronas entre contextos se resuelven a la URL real si el proveedor es real, y al simulador si no."""
import dataclasses
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import config, gates as G, interconexion, scaffold  # noqa: E402
from forge.archimate import build_ir  # noqa: E402
from forge.config import Domain  # noqa: E402
from forge.manifest import build_manifest, service_env  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ARCHI = ROOT.parent / "diseno/modelo/drones-mantenimiento.archimate"
DOCS = ROOT.parent / "diseno"
ALL = {k: {"usar": True} for k in ("cqrs", "pipeline", "memento", "state", "specification", "outbox", "eventos", "acl", "cache", "cifrado")}


def dom(ctx, lang, arch, port):
    return Domain(ctx, lang, arch, "microservicio", "postgresql", port, patterns=dict(ALL))


@pytest.fixture(scope="module")
def ir():
    return build_ir(ARCHI, DOCS)


@pytest.fixture
def intervenciones():
    return dom("Intervenciones", "csharp", "clean-ddd", 5101)


@pytest.fixture
def habilitacion():
    return dom("Habilitación de Personal", "java", "hexagonal", 5103)


def test_env_var_name_is_stable_and_accent_free():
    assert interconexion.env_var("Habilitación de Personal") == "HABILITACION_DE_PERSONAL_API_URL"
    assert interconexion.env_var("Notificaciones") == "NOTIFICACIONES_API_URL"


def test_sync_links_come_from_the_model_for_any_pair_of_contexts(ir):
    links = interconexion.sync_links(ir)
    got = {(l["downstream"], l["upstream"], l["slug"]) for l in links}
    assert ("Intervenciones", "Habilitación de Personal", "consulta-de-habilitacion") in got
    assert all(l["env"].endswith("_API_URL") for l in links)


def test_simulated_provider_resolves_to_the_simulator(ir, intervenciones):
    url = interconexion.api_urls(ir, intervenciones, [intervenciones])
    assert url["HABILITACION_DE_PERSONAL_API_URL"] == "http://simulators:5110/api/habilitacion-de-personal"


def test_real_provider_resolves_to_its_own_service_and_stops_being_simulated(ir, intervenciones, habilitacion):
    url = interconexion.api_urls(ir, intervenciones, [intervenciones, habilitacion])
    assert url["HABILITACION_DE_PERSONAL_API_URL"] == "http://habilitacion-de-personal:5103/api"


def test_consumer_keeps_its_acl_items_even_when_the_provider_becomes_real(ir, intervenciones, habilitacion):
    for real in ([intervenciones], [intervenciones, habilitacion]):
        names = {i["name"] for i in build_manifest(ir, real)["items"] if i["domain"] == "Intervenciones" and i["kind"] in ("acl_port", "acl_adapter")}
        assert names == {"IConsultaDeHabilitacion", "ConsultaDeHabilitacionAdapter"}, real


def test_real_provider_must_expose_the_route_the_consumers_expect(ir, intervenciones, habilitacion):
    solo = build_manifest(ir, [intervenciones])["items"]
    assert not any(i["domain"] == "Habilitación de Personal" for i in solo)
    items = [i for i in build_manifest(ir, [intervenciones, habilitacion])["items"]
             if i["domain"] == "Habilitación de Personal" and i["kind"] == "route" and "consulta-de-habilitacion" in i["name"]]
    assert items and items[0]["required"] and items[0]["layer"] == "api"


def test_service_env_carries_the_api_urls_and_keeps_simulators_url_for_old_outputs(ir, intervenciones, habilitacion):
    env = service_env(intervenciones, api_urls=interconexion.api_urls(ir, intervenciones, [intervenciones, habilitacion]))
    assert env["HABILITACION_DE_PERSONAL_API_URL"].startswith("http://habilitacion-de-personal:5103")
    assert env["SIMULATORS_URL"] == "http://simulators:5110"


def test_platform_compose_and_simulators_follow_who_is_real(ir, intervenciones, habilitacion, tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path / "out")
    outs = {}
    for label, real in (("sim", [intervenciones]), ("real", [intervenciones, habilitacion])):
        cfg.domains = real
        target = tmp_path / label
        scaffold.platform(cfg, ir, build_manifest(ir, real), target, "../services", True)
        outs[label] = ((target / "docker-compose.yml").read_text(encoding="utf-8"),
                       json.loads((target / "simulators/simulators.json").read_text(encoding="utf-8")))
    assert 'HABILITACION_DE_PERSONAL_API_URL: "http://simulators:5110/api/habilitacion-de-personal"' in outs["sim"][0]
    assert 'HABILITACION_DE_PERSONAL_API_URL: "http://habilitacion-de-personal:5103/api"' in outs["real"][0]
    assert any(a["context"] == "Habilitación de Personal" for a in outs["sim"][1]["apis"])
    assert not any(a["context"] == "Habilitación de Personal" for a in outs["real"][1]["apis"])      # lo real no se simula


def _svc(tmp_path, slug, files):
    for rel, text in files.items():
        f = tmp_path / "services" / slug / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")


def test_gate_flags_a_consumer_still_pointing_at_the_simulator_and_a_provider_without_the_route(ir, intervenciones, habilitacion, tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path)
    _svc(tmp_path, "intervenciones", {"src/Adapter.cs": 'var u = Environment.GetEnvironmentVariable("SIMULATORS_URL");'})
    _svc(tmp_path, "habilitacion-de-personal", {"src/main/java/X.java": "class X {}"})
    res = {g.name: g for g in G.interconnect_gates(cfg, ir, [intervenciones, habilitacion])}
    consumer, provider = res["interconexión: consumidores usan la URL del proveedor"], res["interconexión: proveedores exponen la ruta del contrato"]
    assert not consumer.ok and "HABILITACION_DE_PERSONAL_API_URL" in consumer.detail and "Intervenciones" in consumer.detail
    assert not provider.ok and "/api/consulta-de-habilitacion" in provider.detail


def test_gate_passes_when_consumer_reads_the_variable_and_provider_exposes_the_route(ir, intervenciones, habilitacion, tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path)
    _svc(tmp_path, "intervenciones", {"src/Adapter.cs": 'Environment.GetEnvironmentVariable("HABILITACION_DE_PERSONAL_API_URL")'})
    _svc(tmp_path, "habilitacion-de-personal", {"src/main/java/Api.java": '@PostMapping("/api/consulta-de-habilitacion")'})
    assert all(g.ok for g in G.interconnect_gates(cfg, ir, [intervenciones, habilitacion]))


def test_gate_is_silent_when_every_provider_is_simulated(ir, intervenciones, tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path)
    _svc(tmp_path, "intervenciones", {"src/Adapter.cs": 'GetEnvironmentVariable("SIMULATORS_URL")'})
    assert all(g.ok for g in G.interconnect_gates(cfg, ir, [intervenciones]))            # outputs anteriores siguen válidos


def test_generic_read_only_queries_do_not_demand_a_named_route(ir, intervenciones):
    """Evidencia y Reportes -> Intervenciones es una «Consulta de solo lectura»: no hay operación con nombre que exigirle al proveedor."""
    links = [l for l in interconexion.sync_links(ir) if l["upstream"] == "Intervenciones"]
    assert links and not any(l["explicit"] for l in links)
    assert not any(i["kind"] == "route" and "solo-lectura" in i["name"] for i in build_manifest(ir, [intervenciones])["items"])


def test_explicit_api_operations_are_marked_explicit(ir):
    by = {(l["downstream"], l["upstream"]): l for l in interconexion.sync_links(ir)}
    assert by[("Intervenciones", "Habilitación de Personal")]["explicit"] and by[("Repuestos del Taller", "Notificaciones")]["explicit"]
