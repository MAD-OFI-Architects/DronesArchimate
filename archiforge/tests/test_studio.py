"""Capa sin UI de la TUI: proyectos, inspección de modelo y servicio."""
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import config  # noqa: E402
from forge.credentials import CredentialStore  # noqa: E402
from forge.studio import model, projects, service  # noqa: E402

TOOL = Path(__file__).resolve().parents[1]
ARCHIMATE = TOOL.parent / "diseno/modelo/drones-mantenimiento.archimate"
DOCS = TOOL.parent / "diseno"


@pytest.fixture
def store(tmp_path):
    return projects.ProjectStore(tmp_path / "reg.json", tmp_path / "projects")


@pytest.fixture
def studio(store, tmp_path):
    info = store.create("Drones de prueba", ARCHIMATE, DOCS, projects.AgentSettings(engine="custom", custom_argv=("echo", "{prompt_file}")))
    return service.Studio(store.load(info), CredentialStore(tmp_path / "cred.json"))


# ------------------------------------------------------------------ proyectos
def test_create_generates_a_loadable_forge_toml_and_registers_it(store):
    info = store.create("Mi Proyecto", ARCHIMATE, DOCS, projects.AgentSettings(model="opencode/x"))
    cfg = store.load(info)
    assert info.slug == "mi-proyecto" and cfg.archimate == ARCHIMATE and cfg.docs_dir == DOCS and cfg.agent.model == "opencode/x"
    assert (info.root / "decisiones").is_dir() and (info.root / ".opencode" / "agents").is_dir()
    assert [p.name for p in store.list()] == ["Mi Proyecto"]


@pytest.mark.parametrize("name,path", [("", ARCHIMATE), ("x", TOOL / "README.md"), ("x", TOOL / "no-existe.archimate")])
def test_create_rejects_bad_input(store, name, path):
    with pytest.raises(projects.ProjectError):
        store.create(name, path, None, projects.AgentSettings())


def test_create_refuses_to_overwrite_and_custom_engine_needs_a_command(store):
    store.create("Uno", ARCHIMATE, None, projects.AgentSettings())
    with pytest.raises(projects.ProjectError):
        store.create("Uno", ARCHIMATE, None, projects.AgentSettings())
    with pytest.raises(projects.ProjectError):
        store.create("Dos", ARCHIMATE, None, projects.AgentSettings(engine="custom"))


def test_forget_never_deletes_files(store):
    info = store.create("Uno", ARCHIMATE, None, projects.AgentSettings())
    store.forget(info)
    assert store.list() == [] and info.toml.exists()


# ------------------------------------------------------------------ inspección del modelo
def test_inspect_model_with_docs_is_ready():
    r = model.inspect_model(ARCHIMATE, DOCS)
    assert r.ok and r.totals["contextos"] == 9 and r.totals["comandos"] == 54 and not r.errors


def test_inspect_model_without_docs_explains_what_is_missing():
    r = model.inspect_model(ARCHIMATE, None)
    assert not r.ok and r.errors and any("documentos de fase" in h for h in r.hints)


def test_inspect_model_never_raises_on_foreign_files(tmp_path):
    bad = tmp_path / "roto.archimate"
    bad.write_text("<no es xml", encoding="utf-8")
    empty = tmp_path / "vacio.archimate"
    empty.write_text('<?xml version="1.0"?><archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" name="x"/>', encoding="utf-8")
    assert "XML" in model.inspect_model(bad).errors[0]
    assert not model.inspect_model(empty).ok
    assert not model.inspect_model(tmp_path / "nada.archimate").ok
    assert not model.inspect_model(TOOL / "README.md").ok


# ------------------------------------------------------------------ servicio
def test_rows_list_every_context_and_flag_the_undecided(studio):
    rows = studio.rows()
    assert len(rows) == 9 and all(not r.decided and r.status == "se simula" for r in rows)
    inter = next(r for r in rows if r.context == "Intervenciones")
    assert inter.aggregates >= 1 and inter.commands >= 9


def choose(studio, context, lang="python", arch="hexagonal", style="microservicio", db="postgresql", patterns=(), **rationale):
    """Lo que hace el arquitecto en el formulario: elegir todo explícitamente."""
    d = studio.draft(context)
    d.language, d.architecture, d.style, d.database = lang, arch, style, db
    for p in patterns:
        d.patterns[p] = {"usar": True}
    d.rationale = dict(rationale)
    return d


def test_blank_draft_preselects_nothing_and_offers_the_whole_catalog(studio):
    d = studio.draft("Intervenciones")
    assert (d.language, d.architecture, d.style, d.database) == ("", "", "", "")
    assert d.port == 5101 and not any(v["usar"] for v in d.patterns.values()) and set(d.patterns) == set(studio.catalog())
    ref = studio.reference()
    assert [r["id"] for r in ref] == list(studio.catalog()) and all({"nombre", "que_es", "cuando_si", "cuando_no", "costo"} <= r.keys() for r in ref)
    assert not any("recomend" in str(r).lower() or "evaluaci" in str(r).lower() for r in ref)


def test_save_requires_every_choice_then_persists_exactly_what_was_chosen(studio):
    with pytest.raises(service.StudioError) as e:
        studio.save(studio.draft("Intervenciones"))
    assert all(w in str(e.value) for w in ("el lenguaje", "la arquitectura interna", "el estilo de servicio", "la base de datos"))
    d = choose(studio, "Intervenciones", lang="csharp", arch="clean-ddd", db="mongodb", lenguaje="porque sí")          # ningún patrón
    path = studio.save(d)
    saved = studio.draft("Intervenciones")
    assert path.exists() and next(r for r in studio.rows() if r.context == "Intervenciones").decided
    assert (saved.language, saved.database) == ("csharp", "mongodb") and not any(v["usar"] for v in saved.patterns.values())
    assert saved.rationale["lenguaje"] == "porque sí"
    assert studio.draft("Repuestos del Taller").port == 5102                       # el siguiente puerto libre


def test_pattern_dependencies_are_reported_not_auto_selected(studio):
    d = choose(studio, "Intervenciones", patterns=("pipeline",))                   # pipeline requiere cqrs
    with pytest.raises(service.StudioError) as e:
        studio.save(d)
    assert "cqrs" in str(e.value) and not studio.draft("Intervenciones").uses("pipeline")


def test_policy_findings_and_requirements_exist_only_when_the_project_declares_them(studio):
    assert studio.policy_findings() == []                                          # sin [policy]: nada que mostrar ni exigir
    assert studio.check(choose(studio, "Intervenciones"))[0] == []                 # ni siquiera la caché
    studio.cfg.policy = {"required_patterns": ["cache"], "min_domains": 2}
    errors, _ = studio.check(choose(studio, "Intervenciones"))
    assert any("política" in e.lower() and "caché" in e.lower() for e in errors)
    assert studio.policy_findings() and all(f[0] in "✓✗" for f in studio.policy_findings())


def test_progress_lists_every_stage_pending_before_building(studio):
    studio.save(choose(studio, "Intervenciones", lang="csharp", arch="clean-ddd", db="mongodb"))
    rows = studio.progress(studio.cfg.domains[0])
    assert rows[0].id == "S00-ir" and all(r.status == "pending" for r in rows) and any(r.id == "S40-microfrontend" for r in rows)


def test_build_requires_domains_and_can_be_cancelled(studio):
    with pytest.raises(service.StudioError):
        studio.start_build([], print)
    studio.save(choose(studio, "Repuestos del Taller"))
    lines = []
    h = studio.start_build(studio.cfg.domains, lines.append, laps=1)
    h.cancel()
    h.wait(30)
    assert not h.running and h.results and any("cancelada" in l or "S00" in l for l in lines)
    assert all(l.startswith("[repuestos-del-taller]") for l in lines)


def test_agent_env_comes_from_the_credential_store(studio):
    studio.creds.set("ANTHROPIC_API_KEY", "sk-ant-xxxxxxxx")
    assert studio.agent_env() == {"ANTHROPIC_API_KEY": "sk-ant-xxxxxxxx"}


def test_weak_argument_rejects_drafts_and_short_text():
    from forge import gates
    assert gates.weak_argument("Ejemplo: C# por tipado fuerte y soporte de DDD en el dominio.")
    assert gates.weak_argument("corto") and gates.weak_argument("") and gates.weak_argument(None)
    assert not gates.weak_argument("Elegimos C# por el tipado fuerte y el soporte de DDD que necesita el agregado.")


def test_check_warns_about_draft_justifications_only_when_the_project_asks_for_them(studio):
    d = choose(studio, "Intervenciones", lenguaje="Ejemplo: C# por tipado fuerte y soporte de DDD.",
               estilo="Elegimos microservicio porque publica y consume eventos del ciclo de la OT.")
    assert studio.check(d)[1] == []                                                # producto neutral: no regaña
    studio.cfg.policy = {"require_justifications": True}
    _, warns = studio.check(d)
    assert any("«lenguaje»" in w and "borrador" in w for w in warns) and not any("«estilo»" in w and "borrador" in w for w in warns)
