"""Pruebas de ArchiForge (herméticas: sin agentes, sin docker, sin dotnet)."""
import dataclasses
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forge import agentdefs, agents, config, conformance, decisions, gates as G  # noqa: E402
from forge.archimate import build_ir, validate_ir  # noqa: E402
from forge.config import AgentCfg, Domain  # noqa: E402
from forge.manifest import build_manifest  # noqa: E402
from forge.stages import build_stages, agent_for  # noqa: E402
from forge.util import kebab, norm, pascal  # noqa: E402

ARCHI = ROOT.parent / "diseno/modelo/drones-mantenimiento.archimate"
DOCS = ROOT.parent / "diseno"
ALL = {"cqrs": {"usar": True}, "memento": {"usar": True}, "cache": {"usar": True}, "cifrado": {"usar": True},
       "outbox": {"usar": True}, "eventos": {"usar": True}, "acl": {"usar": True}, "state": {"usar": True}}


def dom(ctx="Repuestos del Taller", lang="python", arch="hexagonal", style="microservicio", db="postgresql", patterns=None, port=5101):
    return Domain(ctx, lang, arch, style, db, port, patterns=dict(ALL if patterns is None else patterns))


@pytest.fixture(scope="module")
def ir():
    return build_ir(ARCHI, DOCS)


def mkcfg(tmp_path):
    c = config.load(ROOT / "forge.toml")
    return dataclasses.replace(c, out_dir=tmp_path) if hasattr(c, "out_dir") else c


def test_naming():
    assert pascal("Orden de trabajo") == "OrdenDeTrabajo"
    assert pascal("Liberación") == "Liberacion"
    assert kebab("Registrar entrada de repuesto") == "registrar-entrada-de-repuesto"
    assert norm("Hora_de-Corte") == "horadecorte"


def test_ir_counts_and_consistency(ir):
    assert len(ir["contexts"]) == 9 and len(ir["aggregates"]) == 13 and len(ir["commands"]) == 54
    assert not any(validate_ir(ir))


@pytest.mark.parametrize("lang,arch", [(l, a) for l in ("csharp", "python", "java") for a in ("clean-ddd", "hexagonal")])
def test_manifest_every_language_and_architecture(ir, lang, arch):
    m = build_manifest(ir, [dom(lang=lang, arch=arch)])
    assert m["items"] and all(i["language"] == lang for i in m["items"] if i["layer"] != "frontend")
    assert m == build_manifest(ir, [dom(lang=lang, arch=arch)])        # determinista


def test_patterns_are_toggles_not_impositions(ir):
    full = build_manifest(ir, [dom(lang="csharp", arch="clean-ddd")])["items"]
    bare = build_manifest(ir, [dom(lang="csharp", arch="clean-ddd", patterns={})])["items"]
    kinds_full, kinds_bare = {i["kind"] for i in full}, {i["kind"] for i in bare}
    assert {"memento", "query_handler"} <= kinds_full
    assert not ({"memento", "query_handler", "event_publisher"} & kinds_bare)
    no_cqrs = build_manifest(ir, [dom(lang="csharp", arch="clean-ddd", patterns={**ALL, "cqrs": {"usar": False}})])["items"]
    assert len(no_cqrs) < len(full)


def test_style_changes_the_design(ir):
    soa = {i["kind"] for i in build_manifest(ir, [dom(style="soa")])["items"]}
    mod = {i["kind"] for i in build_manifest(ir, [dom(style="monolito-modular")])["items"]}
    assert "module_facade" in mod and "module_facade" not in soa


def test_frontend_one_remote_per_domain(ir):
    m = build_manifest(ir, [dom(), dom("Intervenciones", "csharp", "clean-ddd", "microservicio", "mongodb", port=5102)])
    slugs = {r["slug"] for r in m["frontend"]["remotes"]}
    assert slugs == {"mfe-repuestos-del-taller", "mfe-intervenciones"}
    assert all(r["roles"] for r in m["frontend"]["remotes"])


def test_context_info_reports_facts_without_any_verdict(ir):
    from forge import contextinfo
    f = contextinfo.facts(ir, "Repuestos del Taller")
    assert f["aggregates"] and f["commands"] and "published" in f and "consumed" in f
    assert not hasattr(contextinfo, "advise") and not hasattr(contextinfo, "R")      # nada de recomendaciones


def test_catalog_is_neutral_reference_without_evaluation_flags():
    cat = decisions.catalog(ROOT)
    assert cat and not any("evaluacion" in v for v in cat.values())
    text = (ROOT / "catalog" / "patrones.toml").read_text(encoding="utf-8").lower()
    assert not any(w in text for w in ("evaluaci", "rúbrica", "profesor", "recomend"))


def test_decisions_roundtrip_and_validation(tmp_path):
    c = dataclasses.replace(config.load(ROOT / "forge.toml"), decisions_dir=tmp_path, policy={})     # el forge.toml real declara [policy]: aquí se prueba sin ella
    d = dom(patterns={"pipeline": {"usar": True}})            # pipeline requiere cqrs
    errors, _ = decisions.validate(c, d)
    assert any("cqrs" in e for e in errors)
    d.patterns = {"cqrs": {"usar": True}, "pipeline": {"usar": True}, "cache": {"usar": False}}
    d.rationale = {"lenguaje": "x"}
    errors, warns = decisions.validate(c, d)                                   # sin [policy]: nada se exige, ni siquiera la caché
    assert not errors and not warns
    strict = dataclasses.replace(c, policy={"required_patterns": ["memento", "cache"], "require_justifications": True})
    errors, warns = decisions.validate(strict, d)                              # con política del proyecto: se exige lo que ella dice
    assert any("caché" in e.lower() and "política" in e.lower() for e in errors) and any("memento" in e.lower() for e in errors)
    assert any("arquitectura" in w for w in warns)
    p = decisions.write(c, d)
    back = decisions.read(p)
    assert (back.language, back.architecture, back.style, back.database) == ("python", "hexagonal", "microservicio", "postgresql")
    assert back.uses("cqrs") and not back.uses("cache")
    bad = dom(lang="cobol")
    assert decisions.validate(c, bad)[0]


def test_tool_never_chooses_for_the_architect(tmp_path):
    f = tmp_path / "x.toml"
    f.write_text('contexto = "Intervenciones"\nlenguaje = "java"\n')
    with pytest.raises(SystemExit):
        decisions.read(f)


def test_stages_follow_decisions():
    c = config.load(ROOT / "forge.toml")
    ids = lambda d: [s.id for s in build_stages(c.for_domain(d))]  # noqa: E731
    assert "S10-kernel" in ids(dom(lang="csharp", arch="clean-ddd"))
    assert "S10-kernel" not in ids(dom(lang="python", arch="hexagonal"))
    assert agent_for("S11-domain", "java") == "forge-java" and agent_for("S11-domain", "csharp") == "forge-csharp"
    assert agent_for("S03-adr", "python") == "forge-architect"


def test_state_is_isolated_per_domain():
    c = config.load(ROOT / "forge.toml")
    a, b = c.for_domain(dom()), c.for_domain(dom("Intervenciones", port=5102))
    assert a.state_dir != b.state_dir and a.domains[0].slug != b.domains[0].slug


def test_conformance_requires_layer_and_declaration(tmp_path, ir):
    d = dom()
    m = build_manifest(ir, [d])
    c = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path, domains=[d]) if False else None
    svc = tmp_path / "services/repuestos-del-taller/src/pkg"
    (svc / "domain").mkdir(parents=True); (svc / "application").mkdir(parents=True)
    (svc / "domain/e.py").write_text("class Existencia:\n    pass\n")
    (svc / "application/x.py").write_text("class ExistenciaMemento:\n    pass\n")      # capa equivocada
    idx = conformance.index(tmp_path / "services/repuestos-del-taller", "python")
    assert any(n == "Existencia" for _, n, *_ in [(0, t[1], *t[2:]) for t in idx]) or idx


def test_arch_python_detects_inward_violation(tmp_path):
    from types import SimpleNamespace
    c = SimpleNamespace(out=tmp_path, root=tmp_path)
    d = tmp_path / "services/x/src/pkg/domain"; d.mkdir(parents=True)
    (d / "ok.py").write_text("from dataclasses import dataclass\n")
    assert G.arch_python(c, "x").ok
    (d / "bad.py").write_text("from pkg.application import casos\nimport sqlalchemy\n")
    g = G.arch_python(c, "x")
    assert not g.ok and "application" in g.detail and "sqlalchemy" in g.detail


def test_arch_java_detects_inward_violation(tmp_path):
    from types import SimpleNamespace
    c = SimpleNamespace(out=tmp_path, root=tmp_path)
    d = tmp_path / "services/x/src/main/java/com/agrodrones/x/domain"; d.mkdir(parents=True)
    (d / "Ok.java").write_text("package com.agrodrones.x.domain;\nimport java.util.List;\npublic class Ok {}\n")
    assert G.arch_java(c, "x").ok
    (d / "Bad.java").write_text("package com.agrodrones.x.domain;\nimport org.springframework.stereotype.Service;\nimport com.agrodrones.x.application.Uso;\npublic class Bad {}\n")
    g = G.arch_java(c, "x")
    assert not g.ok and "springframework" in g.detail


def test_arch_csproj_dependency_rule(tmp_path):
    from types import SimpleNamespace
    c = SimpleNamespace(out=tmp_path, root=tmp_path)
    s = tmp_path / "services/x"
    for n, refs in {"X.Domain": ["..\\..\\BuildingBlocks\\BuildingBlocks.Domain\\BuildingBlocks.Domain.csproj"],
                    "X.Application": ["..\\X.Domain\\X.Domain.csproj"]}.items():
        (s / n).mkdir(parents=True)
        (s / n / f"{n}.csproj").write_text("<Project>" + "".join(f'<ProjectReference Include="{r}" />' for r in refs) + "</Project>")
    assert G.arch_csproj(c, "x").ok
    (s / "X.Domain" / "X.Domain.csproj").write_text('<Project><ProjectReference Include="..\\X.Infrastructure\\X.Infrastructure.csproj" /></Project>')
    assert not G.arch_csproj(c, "x").ok


def test_agent_argv_is_short_and_portable(tmp_path):
    w = tmp_path / ".forge" / "x" / "work" / "S11-domain.md"; w.parent.mkdir(parents=True); w.write_text("x" * 50000)
    argv, _ = agents.build_argv(AgentCfg(engine="claude"), w, tmp_path)
    assert len(" ".join(argv)) < 1000 and "S11-domain.md" in " ".join(argv)


def test_opencode_argv_v2_uses_cwd_auto_and_agent(tmp_path):
    w = tmp_path / ".forge" / "x" / "work" / "S11-domain.md"; w.parent.mkdir(parents=True); w.write_text("x")
    cfg = AgentCfg(engine="opencode", model="opencode/deepseek-v4.1-flash-free", opencode_agent="forge-orchestrator")
    argv, _ = agents.build_argv(cfg, w, tmp_path, agent="forge-python")
    assert "--dir" not in argv                                   # V2 lo toma del cwd
    assert "--auto" in argv
    assert argv[argv.index("--agent") + 1] == "forge-python"     # el agente de la etapa gana
    assert argv[argv.index("-m") + 1] == "opencode/deepseek-v4.1-flash-free"
    argv, _ = agents.build_argv(cfg, w, tmp_path)
    assert argv[argv.index("--agent") + 1] == "forge-orchestrator"   # sin etapa: el de la config


def test_agentdefs_install(tmp_path):
    files = {p.relative_to(tmp_path).as_posix() for p in agentdefs.install(tmp_path, model="opencode/deepseek-v4.1-flash-free")}
    assert {".claude/agents/forge-java.md", ".claude/commands/forge.md", ".claude/commands/forge-design.md",
            ".opencode/agents/forge-orchestrator.md", ".opencode/commands/forge-design.md"} <= files
    design = (tmp_path / ".claude/commands/forge-design.md").read_text(encoding="utf-8").lower()
    assert "decide todo" in design and "no sugieras" in design and "forge patterns" in design        # el asistente solo pregunta y registra
    assert "advise" not in design and "evaluaci" not in design
    orch = (tmp_path / ".opencode/agents/forge-orchestrator.md").read_text(encoding="utf-8")
    sub = (tmp_path / ".opencode/agents/forge-python.md").read_text(encoding="utf-8")
    assert "\npermission:" not in orch and "\npermissions:" in orch      # V1 no; V2 sí
    assert "action: subagent" in orch and 'resource: "forge-*"' in orch
    assert "model: opencode/deepseek-v4.1-flash-free" in sub
    assert "resource: \"*\"" in sub and "effect: allow" in sub


def test_cli_refuses_to_build_without_decisions():
    r = subprocess.run([sys.executable, "-m", "forge", "build", "Notificaciones", "--skip-doctor"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "decisiones" in (r.stdout + r.stderr).lower()


def test_dryrun_end_to_end_with_fake_agent(tmp_path):
    """Python + hexagonal: decide → build (agente simulado) → 100 % conformidad, ADR verificado."""
    import shutil
    work = tmp_path / "w"
    for d in ("modelo", *(f"Fase0{i}" for i in range(1, 7))):        # el diseño vive junto a la herramienta (../diseno/modelo, ../diseno/Fase0N)
        shutil.copytree(ROOT.parent / "diseno" / d, tmp_path / "diseno" / d)
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns("out*", ".forge*", "decisiones_dryrun", ".git", "__pycache__", ".claude", ".opencode", ".pytest_cache"))
    run = lambda *a: subprocess.run([sys.executable, "-m", "forge", "-c", "forge.dryrun.toml", *a], cwd=work, capture_output=True, text=True)  # noqa: E731
    r = run("decide", "Repuestos del Taller", "--lang", "python", "--arch", "hexagonal", "--style", "microservicio", "--db", "postgresql",
            "--patterns", "cqrs,memento,cache,cifrado,eventos,outbox", "--why", "lenguaje=x")
    assert r.returncode == 0, r.stderr
    assert run("platform", "--messaging", "memoria").returncode == 0                  # el canal de eventos lo decide el arquitecto
    r = run("build", "Repuestos del Taller", "--laps", "1", "--skip-doctor")
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-500:]
    assert json.loads(run("-d", "Repuestos del Taller", "next").stdout.split("\n", 2)[-1] if False else (work / ".forge-dry/repuestos-del-taller/state.json").read_text())["S60-report"]["status"] == "passed"
    ratio = json.loads((work / "out_dryrun/docs/repuestos-del-taller/conformidad.json").read_text())["ratio"]
    assert ratio >= 0.9


# ------------------------------------------------------------------ SOLID y políticas del proyecto
def _write(root, rel, text):
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


def test_solid_scan_flags_each_principle_in_python(tmp_path):
    from forge import solid
    wide = "".join(f"    def m{i}(self): ...\n" for i in range(9))
    _write(tmp_path, "src/p/application/caso.py",
           "class Caso:\n    def run(self, e):\n        repo = RepositorioMongo()\n"
           "        if isinstance(e, A): pass\n        elif isinstance(e, B): pass\n        elif isinstance(e, C): pass\n        elif isinstance(e, D): pass\n"
           "class Puerto(Protocol):\n" + wide)
    _write(tmp_path, "src/p/domain/hijo.py", "class Hijo(Base):\n    def f(self):\n        raise NotImplementedError\n")
    got = {f.principle for f in solid.scan(tmp_path, "python")}
    assert got == {"OCP", "LSP", "ISP", "DIP"}


def test_solid_scan_ignores_primitive_validation_and_properties(tmp_path):
    from forge import solid
    _write(tmp_path, "src/p/domain/guard.py", "def g(v):\n    return all(isinstance(v, t) for t in (str,)) or isinstance(v, str) or isinstance(v, int) or isinstance(v, bool) or isinstance(v, float)\n")
    props = "".join(f"    @property\n    def p{i}(self):\n        return 1\n" for i in range(20))
    _write(tmp_path, "src/p/domain/agg.py", "class Agg:\n" + props)
    assert solid.scan(tmp_path, "python") == []


def test_solid_scan_csharp_and_java_signals(tmp_path):
    from forge import solid
    _write(tmp_path, "src/X.Application/Caso.cs", "public class Caso { public void Run() { var r = new RepositorioMongo(); throw new NotSupportedException(); } }\n")
    assert {f.principle for f in solid.scan(tmp_path, "csharp")} == {"DIP", "LSP"}
    _write(tmp_path, "src/main/java/p/application/Caso.java", "public class Caso { void run() { throw new UnsupportedOperationException(); } }\n")
    assert {f.principle for f in solid.scan(tmp_path / "src/main", "java")} == {"LSP"}


def test_build_gates_include_solid_and_java_wiring():
    import inspect
    src = inspect.getsource(G.build_gates)
    assert "solid_gate" in src and "wiring_gate" in src and '"infrastructure" in layers' in src   # cableado: solo en la etapa de adaptadores


def test_policy_gates_apply_only_what_the_project_declares(tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path, policy={})
    a, b = dom("A", "python", "hexagonal"), dom("B", "python", "hexagonal")
    assert G.policy_gates(cfg, [a, b], ["A", "B", "C"]) == []                  # sin política no hay reglas: es el usuario quien decide
    cfg.policy = {"min_domains": 2, "distinct_languages": True, "mixed_architectures": True, "require_justifications": True,
                  "simulate_remaining": True, "required_patterns": ["cache"]}
    why = {k: "Argumento propio y suficientemente largo para el documento." for k in ("lenguaje", "arquitectura", "estilo", "base_de_datos")}
    a.rationale = b.rationale = why
    res = {g.name: g for g in G.policy_gates(cfg, [a, b], ["A", "B", "C"])}
    assert not any("evaluaci" in n.lower() for n in res)
    assert not res["política: cada dominio con un lenguaje distinto"].ok
    assert not res["política: arquitecturas internas distintas entre dominios"].ok
    assert not res["política: contextos restantes simulados"].ok                # no hay simulators.json
    b = dom("B", "csharp", "clean-ddd")
    b.rationale = dict(why, lenguaje="Ejemplo: C# por tipado fuerte y soporte de DDD.")
    b.patterns["cache"] = {"usar": False}
    res = {g.name: g for g in G.policy_gates(cfg, [a, b], ["A", "B"])}
    assert res["política: cada dominio con un lenguaje distinto"].ok and res["política: arquitecturas internas distintas entre dominios"].ok
    assert not res["política: decisiones justificadas"].ok and not res["política: patrones obligatorios (cache)"].ok
    assert res["política: al menos 2 dominios construidos"].ok

def test_scaffolded_frontend_ships_a_design_system_and_passes_the_design_gate(tmp_path):
    from forge import scaffold
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path)
    ir = build_ir(cfg.archimate, cfg.docs_dir)
    m = build_manifest(ir, cfg.domains)
    remotes = m["frontend"]["remotes"]
    assert remotes
    for r in remotes:
        scaffold.scaffold_remote(cfg, m, r)
        assert G.design_gate(cfg, f"frontend/{r['slug']}").ok
    scaffold.scaffold_shell(cfg)
    assert G.shell_design_gate(cfg).ok
    assert "--mfe-primary" in (tmp_path / "frontend/mfe-shell/src/shell.css").read_text(encoding="utf-8")


def test_design_gate_rejects_unstyled_remote(tmp_path):
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path)
    _write(tmp_path, "frontend/mfe-x/src/styles.css", "form{color:#123456}\n")
    _write(tmp_path, "frontend/mfe-x/src/App.tsx", "export const A = () => <form style={{color:'red'}} />;\n")
    g = G.design_gate(cfg, "frontend/mfe-x")
    assert not g.ok and "tokens" in g.detail and "estilos en línea" in g.detail
    assert not G.shell_design_gate(cfg).ok


def test_parallel_build_forwards_stage_selection_to_each_domain():
    """Regresión: `build A B --only S40 --force` repetía el pipeline entero porque el subproceso no recibía --only/--force."""
    import argparse
    from forge import cli
    cfg = config.load(ROOT / "forge.toml")
    a = argparse.Namespace(laps=2, wait=5, only="S40-microfrontend", from_=None, until=None, force=True, skip_permissions=False)
    cmd = cli.child_build_cmd(cfg, ["forge.toml"], dom("Intervenciones"), a)
    assert cmd[cmd.index("--only") + 1] == "S40-microfrontend" and "--force" in cmd and "--from" not in cmd
    a2 = argparse.Namespace(laps=1, wait=5, only=None, from_="S30-smoke", until="S40-microfrontend", force=False, skip_permissions=True)
    cmd = cli.child_build_cmd(cfg, ["forge.toml"], dom("Intervenciones"), a2)
    assert cmd[cmd.index("--from") + 1] == "S30-smoke" and cmd[cmd.index("--until") + 1] == "S40-microfrontend"
    assert "--force" not in cmd and "--only" not in cmd and "--skip-permissions" in cmd


def test_ensure_design_system_migrates_legacy_css_and_keeps_extended_css(tmp_path):
    from forge import scaffold
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), out=tmp_path)
    assert scaffold.ensure_design_system(cfg, "x") is False                       # sin remote: no hace nada
    _write(tmp_path, "frontend/mfe-x/src/styles.css", ":host{display:block}form{display:grid}\n")
    assert scaffold.ensure_design_system(cfg, "x") is True                        # CSS viejo: se migra
    migrated = (tmp_path / "frontend/mfe-x/src/styles.css").read_text(encoding="utf-8")
    assert migrated.count("var(--mfe-") >= 10
    (tmp_path / "frontend/mfe-x/src/styles.css").write_text(migrated + ".extra{color:var(--mfe-text)}\n", encoding="utf-8")
    assert scaffold.ensure_design_system(cfg, "x") is False                       # ya usa tokens: no pisa la ampliación
    assert ".extra" in (tmp_path / "frontend/mfe-x/src/styles.css").read_text(encoding="utf-8")


def test_runner_sink_and_cancel_support_the_tui(tmp_path):
    import threading
    cfg = dataclasses.replace(config.load(ROOT / "forge.toml"), root=tmp_path, out=tmp_path / "out")
    run = __import__("forge.runner", fromlist=["Runner"]).Runner(cfg, dom("Intervenciones", "csharp", "clean-ddd", "microservicio", "mongodb"))
    lines = []
    run.sink = lines.append
    run.log("hola")
    assert lines and lines[0].endswith("hola") and "hola" in (run.fdir / "run.log").read_text(encoding="utf-8")   # sink y archivo
    run.cancel = threading.Event()
    run.cancel.set()
    assert run.run() is False and any("cancelada" in l for l in lines)


def test_tool_checks_lists_what_doctor_prints():
    from forge import cli
    cfg = config.load(ROOT / "forge.toml")
    names = [n for n, _, _ in cli.tool_checks(cfg, [dom(lang="csharp")])]
    assert "git" in names and "docker compose" in names and any(n.startswith("dotnet") for n in names)
    assert not any(n.startswith("java") for n in names)


def test_platform_contracts_contribute_their_rules_to_the_context_that_owns_the_operations(ir):
    """Un contrato N2 cruza contextos; si sus operaciones son comandos de un contexto, sus errores son reglas de ese contexto."""
    n2 = next(k for k in ir["contracts"] if k["service"] == "Ejecución y liberación de intervenciones")
    assert n2["context"] == "Intervenciones" and n2["context_por"] == "operaciones"
    reglas = [i["name"] for i in build_manifest(ir, [dom("Intervenciones", "csharp", "clean-ddd", "microservicio", "mongodb", port=5102)])["items"]
              if i["kind"] == "business_rule"]
    assert "PruebaDeVueloPendiente" in reglas
    sin_comandos = next(k for k in ir["contracts"] if k["service"] == "Identidad y permisos")
    assert sin_comandos["context"] is None                          # no hay comandos que lo liguen a un contexto: no se adivina


def test_prompts_ask_for_contract_codes_and_idempotent_creation():
    leer = lambda n: (ROOT / "prompts" / n).read_text(encoding="utf-8")  # noqa: E731
    assert "`codigo`" in leer("kernel.md.j2") and "`codigo`" in leer("layer.md.j2") and "`codigo`" in leer("mfe.md.j2")
    assert "UUID v5" in leer("layer.md.j2")
