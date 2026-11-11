"""Guías de construcción por decisión (arquitectura, estilo, SOLID) y el gate de estilo microservicio."""
import dataclasses
import json
import sys
from pathlib import Path

import jinja2
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import config, gates as G  # noqa: E402
from forge.archimate import build_ir  # noqa: E402
from forge.config import Domain  # noqa: E402
from forge.manifest import build_manifest  # noqa: E402
from forge.runner import Runner  # noqa: E402

TOOL = Path(__file__).resolve().parents[1]
ARCHI = TOOL.parent / "diseno/modelo/drones-mantenimiento.archimate"
DOCS = TOOL.parent / "diseno"
FORBIDDEN = ("evaluaci", "rúbrica", "profesor", "profe ", "recomend", "aconsej")
KEYS = {"hexagonal": "Puertos de entrada", "clean-ddd": "Anillos", "microservicio": "Base de datos propia", "soa": "Contrato primero",
        "monolito-modular": "un módulo por agregado raíz"}


def env():
    return jinja2.Environment(loader=jinja2.FileSystemLoader(TOOL / "prompts"), undefined=jinja2.StrictUndefined, trim_blocks=True,
                              lstrip_blocks=True, keep_trailing_newline=True)


def dom(arch="hexagonal", style="microservicio", lang="python"):
    return Domain("Repuestos del Taller", lang, arch, style, "postgresql", 5102, patterns={"cqrs": {"usar": True}})


@pytest.mark.parametrize("arch", ["clean-ddd", "hexagonal"])
@pytest.mark.parametrize("style", ["microservicio", "soa", "monolito-modular"])
def test_every_architecture_and_style_has_its_guide_plus_solid(arch, style):
    text = env().get_template("_guias.md.j2").render(d=dom(arch, style))
    assert KEYS[arch].lower() in text.lower() and KEYS[style].lower() in text.lower()
    assert all(p in text for p in ("**SRP**", "**OCP**", "**LSP**", "**ISP**", "**DIP**", "Lo que NO es una violación"))
    assert not any(w in text.lower() for w in FORBIDDEN)


def test_guides_adapt_to_the_chosen_patterns_and_name_the_service():
    with_cqrs = env().get_template("_guias.md.j2").render(d=dom())
    without = env().get_template("_guias.md.j2").render(d=Domain("X", "python", "hexagonal", "microservicio", "postgresql", 5102, patterns={}))
    assert "el mediador es la puerta" in with_cqrs and "un manejador por comando" in without
    assert "«Repuestos del Taller»" in with_cqrs


def test_work_orders_for_build_stages_and_review_include_the_guides(tmp_path):
    base = config.load(TOOL / "forge.toml")
    ir = build_ir(ARCHI, DOCS)
    d = Domain("Intervenciones", "csharp", "clean-ddd", "soa", "mongodb", 5101, patterns={"cqrs": {"usar": True}})
    cfg = dataclasses.replace(base, root=tmp_path, out=tmp_path / "out", domains=[d])
    run = Runner(cfg, d)
    (run.fdir / "ir.json").write_text(json.dumps(ir), encoding="utf-8")
    (run.fdir / "manifest.json").write_text(json.dumps(build_manifest(ir, [d])), encoding="utf-8")
    for stage_id in ("S10-kernel", "S11-domain", "S13-adapters", "S50-verify"):
        text = run.render(next(s for s in run.stages if s.id == stage_id), "").read_text(encoding="utf-8")
        assert "Guía de construcción" in text and "Contrato primero" in text and "Anillos" in text and "**DIP**" in text, stage_id


def test_soa_requires_a_service_catalog_file():
    ir = build_ir(ARCHI, DOCS)
    for style, expected in (("soa", True), ("microservicio", False)):
        names = {i["name"] for i in build_manifest(ir, [dom("hexagonal", style)])["items"] if i["kind"] == "file"}
        assert ("catalogo-de-servicios" in names) is expected, style


# ------------------------------------------------------------------ gate de estilo microservicio
def _svc(tmp_path, files, slug="repuestos-del-taller"):
    for rel, text in files.items():
        f = tmp_path / "services" / slug / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    return dataclasses.replace(config.load(TOOL / "forge.toml"), out=tmp_path, policy={})


MANIFEST = {"domains": {"Repuestos del Taller": {}, "Intervenciones": {}}, "simulated": [{"context": "Plan de Mantenimiento"}]}


def test_microservice_gate_flags_local_state_and_hard_coded_addresses(tmp_path):
    bad = {"src/repuestos_del_taller/application/a.py": "def g(x):\n    with open('/tmp/estado.json', 'w') as f:\n        f.write(x)\n",
           "src/repuestos_del_taller/adapters/outbound/b.py": "URL = 'http://intervenciones:5101/api/orden'\nBUS = 'http://event-bus:5100'\nDB = 'postgresql://postgres:5432/x'\n"}
    cfg = _svc(tmp_path, bad)
    g = G.service_style_gate(cfg, dom(), MANIFEST)
    assert not g.ok
    assert "escribe en el disco local" in g.detail and "a.py" in g.detail
    assert "intervenciones" in g.detail and "event-bus" in g.detail and "postgres" in g.detail and "b.py" in g.detail


def test_microservice_gate_accepts_environment_configuration_and_ignores_tests(tmp_path):
    ok = {"src/repuestos_del_taller/adapters/outbound/b.py": "import os\nURL = os.environ['INTERVENCIONES_API_URL']\nBUS = os.environ['BUS_URL']\n",
          "tests/test_x.py": "URL = 'http://event-bus:5100'\nopen('f.txt', 'w')\n",
          "src/repuestos_del_taller/domain/doc.py": '"""Ver https://refactoring.guru/es/design-patterns/strategy"""\n'}
    cfg = _svc(tmp_path, ok)
    assert G.service_style_gate(cfg, dom(), MANIFEST).ok


def test_style_gate_only_applies_to_microservices_and_runs_in_the_adapters_stage(tmp_path):
    cfg = _svc(tmp_path, {"src/repuestos_del_taller/a.py": "open('x', 'w')\n"})
    assert G.service_style_gate(cfg, dom("hexagonal", "soa"), MANIFEST).ok                     # otros estilos: no aplica
    import inspect
    assert "service_style_gate" in inspect.getsource(G.build_gates)


# ------------------------------------------------------------------ ayudas de los formularios del microfrontend
def _front(tmp_path, files):
    for rel, text in files.items():
        f = tmp_path / "frontend" / "mfe-x" / "src" / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    return dataclasses.replace(config.load(TOOL / "forge.toml"), out=tmp_path)


GOOD_FORM = ("import { CommandForm } from './CommandForm';\nexport const AForm = () => <CommandForm titulo=\"A\" descripcion=\"Hace A.\" "
             "campos={[{ nombre: 'x', etiqueta: 'X', tipo: 'texto', ayuda: 'Qué se escribe, p. ej. 1.' }]} />;\n")
GOOD_CMD = "export interface Campo { nombre: string; etiqueta: string; ayuda?: string }\nexport const C = () => <input aria-describedby=\"a\" />;\n"


def test_hints_gate_requires_description_and_help_for_every_field(tmp_path):
    cfg = _front(tmp_path, {"forms/AForm.tsx": GOOD_FORM, "forms/CommandForm.tsx": GOOD_CMD})
    assert G.hints_gate(cfg, "frontend/mfe-x").ok
    cfg = _front(tmp_path, {"forms/AForm.tsx": GOOD_FORM.replace(" descripcion=\"Hace A.\"", ""), "forms/CommandForm.tsx": GOOD_CMD})
    g = G.hints_gate(cfg, "frontend/mfe-x")
    assert not g.ok and "descripcion" in g.detail
    cfg = _front(tmp_path, {"forms/AForm.tsx": GOOD_FORM.replace(", ayuda: 'Qué se escribe, p. ej. 1.'", ""), "forms/CommandForm.tsx": GOOD_CMD})
    g = G.hints_gate(cfg, "frontend/mfe-x")
    assert not g.ok and "1 campo(s) y solo 0 con `ayuda`" in g.detail
    cfg = _front(tmp_path, {"forms/AForm.tsx": GOOD_FORM, "forms/CommandForm.tsx": "export const C = () => <input />;\n"})
    g = G.hints_gate(cfg, "frontend/mfe-x")
    assert not g.ok and "aria-describedby" in g.detail


def test_scaffolded_frontend_ships_hint_styles_and_a_stub_that_satisfies_the_hints_gate(tmp_path):
    from forge import scaffold
    cfg = dataclasses.replace(config.load(TOOL / "forge.toml"), out=tmp_path)
    ir = build_ir(ARCHI, DOCS)
    m = build_manifest(ir, cfg.domains)
    r = m["frontend"]["remotes"][0]
    scaffold.scaffold_remote(cfg, m, r)
    css = (tmp_path / "frontend" / r["slug"] / "src" / "styles.css").read_text(encoding="utf-8")
    assert ".hint{" in css and ".campo{" in css
    assert G.hints_gate(cfg, f"frontend/{r['slug']}").ok                       # el esqueleto ya nace con ayudas


def test_prompt_and_stage_require_hints():
    text = (TOOL / "prompts" / "mfe.md.j2").read_text(encoding="utf-8")
    assert "Ayudas (obligatorias)" in text and "aria-describedby" in text and "fuera** del `<label>`" in text
    import inspect
    from forge import cli, stages
    assert "hints_gate" in inspect.getsource(stages.build_stages) and "hints_gate" in inspect.getsource(cli.cmd_assemble)
