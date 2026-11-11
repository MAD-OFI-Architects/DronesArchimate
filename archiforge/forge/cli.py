"""CLI de ArchiForge.

Flujo del arquitecto:   advise → decide → build → (en paralelo, en otras máquinas) → assemble → publish
  python -m forge advise "Intervenciones"                      # qué patrones recomienda el modelo y por qué
  python -m forge decide "Intervenciones" --lang java --arch hexagonal --style microservicio --db postgresql --patterns cqrs,memento,cache,cifrado
  python -m forge build  "Intervenciones"                      # ejecuta TODO el dominio hasta terminar y verificar
  python -m forge assemble                                     # une los dominios construidos y corre el humo completo
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import advisor, config, decisions
from . import gates as G
from .archimate import build_ir
from .config import Domain
from .runner import Runner


def _ver(argv: list[str]) -> str:
    exe = shutil.which(argv[0])
    if not exe:
        return ""
    try:
        p = subprocess.run([exe, *argv[1:]], capture_output=True, text=True, timeout=30)
        lines = [l for l in ((p.stdout or "") + (p.stderr or "")).strip().splitlines() if "Picked up" not in l]
        return lines[0] if lines else "ok"
    except Exception:  # noqa: BLE001
        return ""


def doctor(cfg: config.Config, domains: list[Domain] | None = None) -> bool:
    langs = {d.language for d in (domains if domains is not None else cfg.domains)}
    need = [("git", ["git", "--version"]), ("python", [sys.executable, "--version"]), ("node", ["node", "--version"]),
            ("npm", ["npm", "--version"]), ("docker", ["docker", "--version"]), ("docker compose", ["docker", "compose", "version"])]
    if "csharp" in langs:
        need.append(("dotnet (SDK ≥ 8)", ["dotnet", "--version"]))
    if "java" in langs:
        need += [("java (JDK ≥ 17)", ["java", "-version"]), ("maven", ["mvn", "-v"])]
    eng = cfg.agent.engine
    if eng in ("claude", "opencode"):
        need.append((f"agente {eng}", [eng, "--version"]))
    ok = True
    print(f"{'herramienta':22} estado")
    for name, argv in need:
        v = _ver(argv)
        good = bool(v)
        if good and name.startswith("dotnet"):
            good = int(re.match(r"(\d+)", v).group(1)) >= 8
        if good and name == "python":
            good = sys.version_info >= (3, 11)
        if good and name == "node":
            good = int(re.match(r"v(\d+)", v).group(1)) >= 18
        if good and name.startswith("java"):
            m = re.search(r'"?(\d+)', v)
            good = bool(m) and int(m.group(1)) >= 17
        print(f"{'✅' if good else '❌'} {name:20} {v or 'NO ENCONTRADO'}")
        ok &= good
    if not (cfg.archimate.exists() and cfg.guide.exists()):
        print("❌ faltan insumos (archimate o guía de referencia)")
        ok = False
    return ok


def _need_domain(cfg: config.Config, name: str | None) -> Domain:
    if not name:
        raise SystemExit("Indica el dominio: -d \"Nombre\" (p. ej. python -m forge -d \"Intervenciones\" next).")
    d = decisions.find(cfg, name)
    if not d:
        known = ", ".join(x.context for x in cfg.domains) or "ninguno"
        raise SystemExit(f"No hay decisiones para «{name}». Dominios decididos: {known}.\n"
                         f"Decídelas con el agente (/forge-design \"{name}\") o con: python -m forge decide \"{name}\" --lang … --arch … --style … --db …")
    errors, warns = decisions.validate(cfg, d)
    for w in warns:
        print(f"⚠ {w}")
    if errors:
        raise SystemExit("Decisiones inválidas:\n" + "\n".join(f"  ✗ {e}" for e in errors))
    return d


def _context(cfg: config.Config, name: str) -> str:
    names = [c["name"] for c in build_ir(cfg.archimate, cfg.docs_dir)["contexts"]]
    from .util import norm
    key = norm(name)
    hits = [n for n in names if norm(n) == key] or [n for n in names if key in norm(n)]
    if len(hits) != 1:
        raise SystemExit(f"Dominio «{name}» " + ("ambiguo: " + ", ".join(hits) if hits else "no existe en el ArchiMate") + f".\nContextos: {', '.join(names)}")
    return hits[0]


def cmd_decide(cfg: config.Config, a) -> int:
    ctx = _context(cfg, a.name)
    cur = next((d for d in cfg.domains if d.context == ctx), None)
    d = cur or Domain(ctx, a.lang or "", "", "", "", 0)
    for field, val in (("language", a.lang), ("architecture", a.arch), ("style", a.style), ("database", a.db)):
        if val:
            setattr(d, field, val)
    if a.port:
        d.port = a.port
    elif not cur:
        d.port = next(p for p in range(5101, 5300) if p not in {x.port for x in cfg.domains})
    if a.patterns is not None:
        d.patterns = {}
        for tok in [t.strip() for t in a.patterns.split(",") if t.strip()]:
            d.patterns[tok.lstrip("!")] = {"usar": not tok.startswith("!")}
    for item in a.why or []:
        k, _, v = item.partition("=")
        d.rationale[k.strip()] = v.strip()
    missing = [n for n, v in (("--lang", d.language), ("--arch", d.architecture), ("--style", d.style), ("--db", d.database)) if not v]
    if missing:
        raise SystemExit(f"Faltan decisiones: {', '.join(missing)}. La herramienta no elige por ti (mira `python -m forge advise \"{ctx}\"`).")
    errors, warns = decisions.validate(cfg, d)
    if errors:
        raise SystemExit("Decisiones inválidas:\n" + "\n".join(f"  ✗ {e}" for e in errors))
    path = decisions.write(cfg, d)
    print(f"✔ guardado en {path.relative_to(cfg.root)}")
    for w in warns:
        print(f"⚠ {w}")
    return 0


def _domain_status(cfg: config.Config, d: Domain) -> str:
    sf = cfg.root / cfg.state_dir / d.slug / "state.json"
    if not sf.exists():
        return "sin empezar"
    st = json.loads(sf.read_text(encoding="utf-8"))
    from .stages import build_stages
    total = [s.id for s in build_stages(cfg.for_domain(d))]
    done = sum(1 for i in total if st.get(i, {}).get("status") == "passed")
    failed = [i for i in total if st.get(i, {}).get("status") == "failed"]
    return ("✅ completo" if done == len(total) else f"{done}/{len(total)} etapas") + (f" · ❌ {', '.join(failed)}" if failed else "")


def cmd_domains(cfg: config.Config) -> int:
    ir = build_ir(cfg.archimate, cfg.docs_dir)
    decided = {d.context: d for d in cfg.domains}
    print(f"{'Contexto del ArchiMate':28} {'decidido':9} {'lenguaje':8} {'arquitectura':12} {'estilo':16} {'BD':11} estado")
    for c in ir["contexts"]:
        d = decided.get(c["name"])
        if d:
            print(f"{c['name']:28} {'sí':9} {d.language:8} {d.architecture:12} {d.style:16} {d.database:11} {_domain_status(cfg, d)}")
        else:
            print(f"{c['name']:28} {'—':9} (se simula; decide con `forge decide` para construirlo)")
    return 0


def _reopen(run: Runner) -> None:
    """Antes de reintentar: las etapas fallidas u omitidas vuelven a pendiente."""
    for k in [k for k, v in run.state.items() if v.get("status") in ("failed", "skipped")]:
        run.state.pop(k)
    run.save()


def build_one(cfg: config.Config, d: Domain, a) -> int:
    run = Runner(cfg, d, a.skip_permissions)
    for lap in range(1, a.laps + 1):
        if lap > 1:
            _reopen(run)
        run.log(f"=== «{d.context}» · vuelta {lap}/{a.laps} ===")
        if run.run(a.only, a.from_, a.until, a.force):
            run.log(f"✅ «{d.context}» terminado y verificado. Revisa out/docs/{d.slug}/ (verificacion.md, trazabilidad.md, supuestos.md).")
            return 0
        if a.only or lap == a.laps:
            break
        run.log(f"Quedaron etapas sin pasar; reintento en {a.wait}s (límites de cuota, red, etc.)…")
        time.sleep(a.wait)
    return 1


def child_build_cmd(cfg: config.Config, argv0: list[str], d: Domain, a) -> list[str]:
    """Orden del subproceso de un dominio al construir varios en paralelo. Debe reenviar TODAS las opciones de `build`
    que cambian qué se ejecuta (--only/--from/--until/--force); si no, el subproceso repite el pipeline entero."""
    cmd = [sys.executable, "-m", "forge", "-c", str(cfg.root / argv0[0]), "build", d.context, "--skip-doctor", "--laps", str(a.laps),
           "--wait", str(a.wait)]
    for flag, val in (("--only", a.only), ("--from", a.from_), ("--until", a.until)):
        if val:
            cmd += [flag, val]
    if a.force:
        cmd.append("--force")
    if a.skip_permissions:
        cmd.append("--skip-permissions")
    return cmd


def cmd_build(cfg: config.Config, a, argv0: list[str]) -> int:
    doms = [_need_domain(cfg, n) for n in a.names]
    if not a.skip_doctor and cfg.strict_tools and not doctor(cfg, doms):
        print("\nCorrige lo marcado con ❌ (o usa --skip-doctor bajo tu riesgo).")
        return 2
    if len(doms) == 1:
        return build_one(cfg, doms[0], a)

    def launch(d: Domain) -> int:     # cada dominio en su propio proceso: estado, logs y puertos propios
        cmd = child_build_cmd(cfg, argv0, d, a)
        p = subprocess.Popen(cmd, cwd=cfg.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
        for line in p.stdout:  # type: ignore[union-attr]
            print(f"[{d.slug}] {line.rstrip()}", flush=True)
        return p.wait()

    with ThreadPoolExecutor(max_workers=a.jobs or len(doms)) as ex:
        codes = list(ex.map(launch, doms))
    for d, c in zip(doms, codes):
        print(f"{'✅' if c == 0 else '❌'} {d.context}")
    return 0 if not any(codes) else 1


def cmd_assemble(cfg: config.Config, a) -> int:
    from . import scaffold
    from .manifest import build_manifest
    out = cfg.out
    built = [d for d in cfg.domains if (out / d.dir / "forge-domain.json").exists()]
    if not built:
        raise SystemExit("No hay dominios construidos en out/. Primero: python -m forge build \"<Dominio>\"")
    cfg2 = dataclasses.replace(cfg, domains=built, state_dir=f"{cfg.state_dir}/_assemble")
    ir = build_ir(cfg.archimate, cfg.docs_dir)
    manifest = build_manifest(ir, built)
    created = scaffold.assemble_files(cfg2, ir, manifest)
    print(f"Ensamblado de {len(built)} dominio(s): {', '.join(d.context for d in built)} ({len(created)} archivos de plataforma)")
    results = [G.shell_design_gate(cfg2)] + [G.design_gate(cfg2, f"frontend/{p.parent.name}") for p in sorted((out / "frontend").glob("mfe-*/mfe.json"))]
    results += [G.npm_build(cfg2, "frontend/mfe-shell")] + [G.npm_build(cfg2, f"frontend/{p.parent.name}") for p in sorted((out / "frontend").glob("mfe-*/mfe.json"))]
    if "smoke" not in cfg.raw.get("quality", {}).get("skip", []):
        results.append(G.smoke_assembled_gate(cfg2, built))
    if cfg.raw.get("quality", {}).get("enforce_evaluation", True):
        results += G.portfolio_gates(cfg2, built, [c["name"] for c in ir["contexts"]])
    fallos = []
    for g in results:
        if g.ok:
            print(f"✅ {g.name}")
        else:
            print(f"❌ {g.name}:\n{g.detail.strip()}")
            fallos.append(g)
    if fallos:
        log = out / "docs" / "ensamblado-fallo.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("\n\n".join(f"### {g.name}\n{g.detail}" for g in fallos), encoding="utf-8")
        print(f"\nDetalle completo en {log.relative_to(cfg.root) if log.is_relative_to(cfg.root) else log}")
    archs = {(d.language, d.architecture, d.style) for d in built}
    rows = ["# Ensamblado", "", "| Dominio | Lenguaje | Arquitectura | Estilo | BD | Conformidad |", "|---|---|---|---|---|---|"]
    for d in built:
        cj = out / "docs" / d.slug / "conformidad.json"
        conf = f"{json.loads(cj.read_text(encoding='utf-8'))['ratio']:.1%}" if cj.exists() else "—"
        rows.append(f"| {d.context} | {d.language} | {d.architecture} | {d.style} | {d.database} | {conf} |")
    rows += ["", f"Mezcla de lenguajes/arquitecturas/estilos: **{len(archs)}** combinaciones distintas."]
    (out / "docs").mkdir(exist_ok=True)
    (out / "docs" / "ensamblado.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    from .runner import git_lock
    if (out / ".git").exists():
        with git_lock(out):
            subprocess.run(["git", "add", "-A"], cwd=out)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", f"[assemble] {len(built)} dominio(s)"], cwd=out)
    return 0 if all(g.ok for g in results) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="forge", description="ArchiForge: del ArchiMate al software, con el arquitecto decidiendo.")
    ap.add_argument("-c", "--config", default="forge.toml")
    ap.add_argument("-d", "--domain", help="dominio (para next/gate/prepare/bootstrap/status/render/report)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="verifica herramientas e insumos")
    sub.add_parser("domains", help="contextos del ArchiMate, cuáles están decididos y cómo va cada uno")
    ad = sub.add_parser("advise", help="recomienda patrones para un dominio según el modelo (NO decide)")
    ad.add_argument("name"); ad.add_argument("--json", action="store_true")
    de = sub.add_parser("decide", help="registra las decisiones del arquitecto para un dominio (decisiones/<dominio>.toml)")
    de.add_argument("name")
    de.add_argument("--lang", choices=list(config.LANGUAGES)); de.add_argument("--arch", choices=list(decisions.ARCHITECTURES))
    de.add_argument("--style", choices=list(decisions.STYLES)); de.add_argument("--db", choices=list(decisions.DATABASES)); de.add_argument("--port", type=int)
    de.add_argument("--patterns", help="lista separada por comas; «!x» descarta x. Ej.: cqrs,memento,cache,!state")
    de.add_argument("--why", action="append", metavar="CLAVE=TEXTO", help="justificación (lenguaje, base_de_datos, arquitectura, estilo o un patrón)")
    ck = sub.add_parser("check", help="valida las decisiones de un dominio y avisa de lo que la evaluación pide")
    ck.add_argument("name")
    b = sub.add_parser("build", help="construye uno o varios dominios hasta terminar y verificar (reintenta y reanuda solo)")
    b.add_argument("names", nargs="+"); b.add_argument("--jobs", type=int, default=0, help="dominios en paralelo (0 = todos a la vez)")
    b.add_argument("--laps", type=int, default=6); b.add_argument("--wait", type=int, default=900)
    b.add_argument("--only"); b.add_argument("--from", dest="from_"); b.add_argument("--until")
    b.add_argument("--force", action="store_true"); b.add_argument("--skip-doctor", action="store_true")
    b.add_argument("--skip-permissions", action="store_true", help="Claude Code con --dangerously-skip-permissions (SOLO en contenedor/VM desechable)")
    sub.add_parser("assemble", help="une los dominios construidos (compose, gateway, shell de microfrontends) y corre el humo completo")
    sub.add_parser("publish", help="sube out/ al repositorio del producto (git push)")
    sub.add_parser("status", help="estado de las etapas del dominio (-d) o resumen de todos")
    sub.add_parser("report", help="conformidad y trazabilidad del dominio (-d)")
    sub.add_parser("render", help="renderiza las órdenes de trabajo del dominio (-d) en .forge/<dominio>/work/")
    # --- modo nativo: el orquestador es un agente de Claude Code / OpenCode que llama a estos comandos por Bash
    sub.add_parser("bootstrap", help="[modo nativo] S00-S02 del dominio (-d)")
    sub.add_parser("next", help="[modo nativo] siguiente acción para el orquestador-agente (JSON)")
    g = sub.add_parser("gate", help="[modo nativo] puertas de una etapa (código de salida 0 = pasa)")
    g.add_argument("stage"); g.add_argument("--no-record", action="store_true", help="solo informa; no cuenta intento ni cambia el estado")
    pr = sub.add_parser("prepare", help="[modo nativo] renderiza la orden de trabajo de una etapa y muestra su ruta")
    pr.add_argument("stage")
    ia = sub.add_parser("install-agents", help="[modo nativo] genera agentes y comandos /forge, /forge-design para Claude Code y/o OpenCode")
    ia.add_argument("--target", choices=["claude", "opencode", "both"], default="both")
    a = ap.parse_args(argv)
    cfg = config.load(Path(a.config))

    if a.cmd == "install-agents":
        from . import agentdefs
        for f in agentdefs.install(cfg.root, ("claude", "opencode") if a.target == "both" else (a.target,), cfg.agent.model):
            print("escrito", f.relative_to(cfg.root))
        return 0
    if a.cmd == "doctor":
        return 0 if doctor(cfg, [_need_domain(cfg, a.domain)] if a.domain else None) else 1
    if a.cmd == "domains":
        return cmd_domains(cfg)
    if a.cmd == "advise":
        ctx = _context(cfg, a.name)
        ir, cat = build_ir(cfg.archimate, cfg.docs_dir), decisions.catalog(cfg.root)
        print(json.dumps({"facts": advisor.facts(ir, ctx), "patrones": advisor.advise(ir, ctx, cat)}, ensure_ascii=False, indent=2)
              if a.json else advisor.render(ir, ctx, cat))
        return 0
    if a.cmd == "decide":
        return cmd_decide(cfg, a)
    if a.cmd == "check":
        d = _need_domain(cfg, a.name)
        print(f"✔ decisiones de «{d.context}» válidas: {d.language} · {d.architecture} · {d.style} · {d.database} · patrones: "
              f"{', '.join(p for p in d.patterns if d.uses(p)) or 'ninguno'}")
        return 0
    if a.cmd == "build":
        return cmd_build(cfg, a, [a.config])
    if a.cmd == "assemble":
        return cmd_assemble(cfg, a)
    if a.cmd == "publish":
        r = subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=cfg.out)
        return r.returncode
    if a.cmd == "status" and not a.domain:
        return cmd_domains(cfg)

    run = Runner(cfg, _need_domain(cfg, a.domain))
    if a.cmd == "render":
        run.render_all()
        print(f"órdenes de trabajo en {run.fdir.relative_to(cfg.root)}/work/")
    elif a.cmd == "status":
        run.report()
    elif a.cmd == "report":
        run.run(only="S60-report", force=True)
    elif a.cmd == "bootstrap":
        return 0 if run.bootstrap() else 1
    elif a.cmd == "next":
        print(json.dumps(run.next_action(), ensure_ascii=False, indent=2))
    elif a.cmd == "prepare":
        print(run.prepare(run.find(a.stage)).relative_to(cfg.root))
    elif a.cmd == "gate":
        return 0 if run.check(run.find(a.stage), record=not a.no_record) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
