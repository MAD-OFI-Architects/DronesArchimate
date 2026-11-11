"""Orquestador: ejecuta las etapas en orden, con reintentos realimentados por las puertas de calidad."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import jinja2

from . import agents, conformance, decisions, scaffold
from . import gates as G
from .archimate import build_ir, validate_ir
from .config import Config, Domain
from .manifest import build_manifest, summary
from .stages import Stage, agent_for, build_stages
from .util import kebab, pascal


@contextmanager
def git_lock(out: Path, timeout: int = 300):
    """Cerrojo entre procesos (varios dominios en paralelo sobre el mismo out/): un directorio como semáforo."""
    lock = out / ".git" / "forge.lock"
    t0 = time.time()
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if time.time() - t0 > timeout:       # cerrojo huérfano
                shutil.rmtree(lock, ignore_errors=True)
            time.sleep(0.2)
    try:
        yield
    finally:
        shutil.rmtree(lock, ignore_errors=True)


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


class Runner:
    def __init__(self, cfg: Config, domain: Domain, skip_permissions: bool = False, agent_env: dict[str, str] | None = None):
        cfg = cfg.for_domain(domain)          # estado propio en .forge/<dominio>/ y solo ese dominio
        self.cfg = cfg
        self.domain = domain
        self.skip_permissions = skip_permissions
        self.sink = None            # callable(str) opcional: recibe cada línea de log (la TUI) en vez de imprimirla
        self.cancel = None          # threading.Event opcional: detiene el pipeline al terminar la etapa en curso
        self.agent_env = dict(agent_env or {})      # tokens de API: solo se pasan por entorno al agente
        self.fdir = cfg.root / cfg.state_dir
        for sub in ("work", "logs"):
            (self.fdir / sub).mkdir(parents=True, exist_ok=True)
        self.state_file = self.fdir / "state.json"
        self.state = json.loads(self.state_file.read_text(encoding="utf-8")) if self.state_file.exists() else {}
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(cfg.tool_root / "prompts"), keep_trailing_newline=True,
                                      undefined=jinja2.StrictUndefined, trim_blocks=True, lstrip_blocks=True)
        self.stages = build_stages(cfg)
        self._ir = self._manifest = None

    # ---------------------------------------------------------------- utilidades
    def log(self, msg: str) -> None:
        line = f"[{now()}] {msg}"
        if self.sink:
            self.sink(line)
        else:
            print(line, flush=True)
        with (self.fdir / "run.log").open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def save(self) -> None:
        self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    @property
    def ir(self) -> dict:
        if self._ir is None:
            self._ir = json.loads((self.fdir / "ir.json").read_text(encoding="utf-8"))
        return self._ir

    @property
    def manifest(self) -> dict:
        if self._manifest is None:
            self._manifest = json.loads((self.fdir / "manifest.json").read_text(encoding="utf-8"))
        return self._manifest

    def git(self, *args: str) -> tuple[int, str]:
        return G.run_cmd(["git", *args], self.cfg.out, timeout=120)

    def ensure_repo(self) -> None:
        if not (self.cfg.out / ".git").exists():
            if self.cfg.repo and not self.cfg.out.exists():
                G.run_cmd(["git", "clone", "-q", self.cfg.repo, str(self.cfg.out)], self.cfg.root, timeout=600)
            self.cfg.out.mkdir(parents=True, exist_ok=True)
            if not (self.cfg.out / ".git").exists():
                self.git("init", "-q")
                self.git("config", "user.name", "ArchiForge")
                self.git("config", "user.email", "archiforge@local")

    def commit(self, stage: Stage) -> None:
        """Commit de la etapa SOLO con los archivos de este dominio (así dos dominios en paralelo, o dos personas, no se pisan)."""
        self.ensure_repo()
        d = self.domain
        paths = [p for p in (f"services/{d.slug}", f"frontend/mfe-{d.slug}", f"docs/{d.slug}", ".gitignore") if (self.cfg.out / p).exists()]
        with git_lock(self.cfg.out):
            if paths:
                self.git("add", "--", *paths)
            code, out = self.git("commit", "-q", "--allow-empty", "-m", f"[{d.slug}] {stage.id}: {stage.title}")
        if code:
            self.log(f"  (git commit omitido: {out.strip()[:120]})")

    # ---------------------------------------------------------------- etapas deterministas
    def det(self, stage: Stage) -> list[G.Gate]:
        cfg = self.cfg
        if stage.id == "S00-ir":
            ir = build_ir(cfg.archimate, cfg.docs_dir)
            errors, warns = validate_ir(ir)
            (self.fdir / "ir.json").write_text(json.dumps(ir, indent=2, ensure_ascii=False), encoding="utf-8")
            self._ir = ir
            self.log(f"  IR: {len(ir['contexts'])} contextos, {len(ir['aggregates'])} agregados, {len(ir['commands'])} comandos, "
                     f"{len(ir['events'])} eventos, {len(ir['policies'])} políticas, {len(ir['contracts'])} contratos")
            return [G.Gate(not errors, "modelo ArchiMate consistente", "\n".join(errors + warns) or "sin errores")]
        if stage.id == "S01-manifest":
            names = {c["name"] for c in self.ir["contexts"]}
            missing = [d.context for d in cfg.domains if d.context not in names]
            if missing:
                return [G.Gate(False, "dominios configurados", f"No existen en el modelo: {missing}")]
            m = build_manifest(self.ir, cfg.domains)
            (self.fdir / "manifest.json").write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
            self._manifest = m
            self.log("  manifiesto: " + json.dumps(summary(m), ensure_ascii=False))
            return [G.Gate(True, "manifiesto", f"{len(m['items'])} símbolos esperados")]
        if stage.id == "S02-scaffold":
            files = scaffold.domain_scaffold(cfg, self.ir, self.manifest)
            d = self.domain
            shutil.copy(scaffold.smoke_dir(cfg, d) / "docs" / "contrato-bus.md", cfg.out / "docs" / d.slug / "contrato-bus.md")
            self.log(f"  {len(files)} archivos generados (servicio, microfrontend y plataforma de humo aislada)")
            return [G.files_gate(cfg, [f"services/{d.slug}/forge-domain.json", f".platform/{d.slug}/docker-compose.yml",
                                       f"docs/{d.slug}/contrato-bus.md"])]
        if stage.id == "S60-report":
            d = self.domain
            res = conformance.check(cfg, self.manifest)
            (cfg.out / "docs" / d.slug).mkdir(parents=True, exist_ok=True)
            (cfg.out / "docs" / d.slug / "trazabilidad.md").write_text(conformance.traceability_markdown(res), encoding="utf-8")
            (cfg.out / "docs" / d.slug / "conformidad.json").write_text(json.dumps(
                {k: res[k] for k in ("total", "ok", "ratio")} | {"faltantes": [m["id"] for m in res["missing"]]}, indent=2, ensure_ascii=False), encoding="utf-8")
            self.log(f"  conformidad de «{d.context}» {res['ok']}/{res['total']} = {res['ratio']:.1%}")
            return [G.conformance_gate(cfg, self.manifest, None, None, cfg.min_conformance, "conformidad con el diseño")]
        raise ValueError(stage.id)

    # ---------------------------------------------------------------- etapas con agente
    def render(self, stage: Stage, feedback: str) -> Path:
        cfg, m, d = self.cfg, self.manifest, self.domain
        ctxs = {c["name"]: c for c in self.ir["contexts"]}
        info = {**ctxs[d.context], **m["domains"][d.context]}
        remotes = [{**r, "commands": [{**c, "form": pascal(c["command"]) + "Form"} for c in r["commands"]]} for r in m["frontend"]["remotes"]]
        layers = stage.params.get("layers", set())
        ctx = {"stage": stage, "scope": stage.scope, "feedback": feedback, "gates_text": stage.gates_text, "cfg": cfg, "d": d, "info": info,
               "ctx": ctxs[d.context], "cat": decisions.catalog(cfg.tool_root), "state_dir": cfg.state_dir, "layer": stage.params.get("layer", ""),
               "items": [i for i in m["items"] if i["domain"] == d.context and i["layer"] in layers],
               "remote": remotes[0] if remotes else None, "remote_slug": f"mfe-{d.slug}", "short": kebab(d.context).split("-")[0]}
        text = self.env.get_template(stage.template).render(**ctx)
        f = self.fdir / "work" / f"{stage.id}.md"
        f.write_text(text, encoding="utf-8")
        return f

    def attempt_agent(self, stage: Stage, n: int, feedback: str) -> list[G.Gate]:
        if stage.id.startswith("S40") and scaffold.ensure_design_system(self.cfg, self.domain.slug):
            self.log("  sistema de diseño: styles.css migrado a los tokens --mfe-* (el remote era anterior al diseño)")
        work = self.render(stage, feedback)
        log = self.fdir / "logs" / f"{stage.id}-intento{n}.log"
        # OpenCode V2: cada etapa se ejecuta con su agente forge-* (lenguaje/especialidad de la etapa).
        agent = agent_for(stage.id, self.domain.language) if self.cfg.agent.engine == "opencode" else None
        who = agent or self.cfg.agent.engine
        self.log(f"  intento {n}: agente «{who}» trabajando (log: {log.relative_to(self.cfg.root)})")
        ok, info = agents.run_agent(self.cfg.agent, work, self.cfg.root, log, self.skip_permissions, agent=agent, env=self.agent_env)
        self.log(f"  agente terminó: {info}")
        gates = stage.gates(self.cfg, self.manifest) if stage.gates else []
        return gates if (ok or gates) else [G.Gate(False, "agente", info)]

    # ---------------------------------------------------------------- bucle principal
    def run_stage(self, stage: Stage) -> bool:
        st = self.state.setdefault(stage.id, {"status": "pending", "attempts": 0})
        st.update(status="running", started=datetime.now().isoformat(timespec="seconds"))
        self.save()
        max_attempts = stage.attempts or (self.cfg.agent.max_attempts if stage.kind == "agent" else 1)
        feedback = ""
        for n in range(1, max_attempts + 1):
            st["attempts"] = n
            t0 = time.time()
            try:
                results = self.det(stage) if stage.kind == "det" else self.attempt_agent(stage, n, feedback)
            except Exception as e:  # noqa: BLE001 — una etapa rota no debe tumbar el resto de la noche
                results = [G.Gate(False, "excepción del orquestador", f"{type(e).__name__}: {e}")]
            bad = [g for g in results if not g.ok]
            for g in results:
                self.log(f"    {'✅' if g.ok else '❌'} {g.name}" + ("" if g.ok else f": {g.detail.strip().splitlines()[0][:150] if g.detail.strip() else ''}"))
            if not bad:
                st.update(status="passed", ended=datetime.now().isoformat(timespec="seconds"), seconds=round(time.time() - t0))
                st.pop("last_error", None)
                self.save()
                self.commit(stage)
                return True
            feedback = "\n\n".join(f"### Puerta fallida: {g.name}\n{g.detail.strip()}" for g in bad)[:9000]
            st["last_error"] = feedback[:3000]
            self.save()
            if stage.kind == "det":
                break
        st.update(status="failed", ended=datetime.now().isoformat(timespec="seconds"))
        self.save()
        self.commit(stage)       # conserva el trabajo parcial para inspeccionarlo
        return False

    def auto_skip(self, stage: Stage) -> bool:
        """Etapa que no aplica (p. ej. sin comandos de usuario → sin microfrontend): se da por pasada dejando el motivo."""
        if not stage.skip_if or not (self.fdir / "manifest.json").exists():
            return False
        why = stage.skip_if(self.cfg, self.manifest)
        if not why:
            return False
        self.state[stage.id] = {"status": "passed", "attempts": 0, "note": why}
        self.save()
        self.log(f"[{stage.id}] no aplica: {why}")
        return True

    def selected(self, only: str | None, from_: str | None, until: str | None) -> list[Stage]:
        ids = [s.id for s in self.stages]
        def idx(x):
            hits = [i for i, v in enumerate(ids) if v == x or v.startswith(x)]
            if not hits:
                raise SystemExit(f"Etapa desconocida: {x}. Disponibles: {', '.join(ids)}")
            return hits[0]
        if only:
            return [self.stages[idx(only)]]
        lo = idx(from_) if from_ else 0
        hi = idx(until) if until else len(ids) - 1
        return self.stages[lo:hi + 1]

    def run(self, only=None, from_=None, until=None, force=False) -> bool:
        self.ensure_repo()
        if self.cfg.agent.engine == "opencode":
            agents.write_opencode_config(self.cfg.root)
        todo = self.selected(only, from_, until)
        self.log(f"=== ArchiForge · {len(todo)} etapas · agente: {self.cfg.agent.engine} ===")
        failed: set[str] = {k for k, v in self.state.items() if v.get("status") in ("failed", "skipped") and not force}
        for stage in todo:
            if self.cancel is not None and self.cancel.is_set():
                self.log(f"Construcción cancelada por el usuario: se detiene antes de «{stage.id}» (lo ya hecho queda guardado).")
                return False
            st = self.state.get(stage.id, {})
            if st.get("status") == "passed" and not force:
                self.log(f"[{stage.id}] ya completada (se omite; usa --force para repetir)")
                continue
            blockers = [d for d in stage.deps if d in failed]
            if blockers and not stage.always:
                self.log(f"[{stage.id}] OMITIDA: dependen de etapas fallidas {blockers}")
                self.state[stage.id] = {"status": "skipped", "attempts": 0, "reason": f"depende de {blockers}"}
                self.save()
                failed.add(stage.id)
                continue
            if self.auto_skip(stage):
                continue
            self.log(f"[{stage.id}] {stage.title}")
            if self.run_stage(stage):
                failed.discard(stage.id)
            else:
                failed.add(stage.id)
                self.log(f"[{stage.id}] FALLÓ tras {self.state[stage.id]['attempts']} intento(s)")
        return self.report()

    # ---------------------------------------------------------------- modo nativo (orquestador = agente)
    def find(self, sid: str) -> Stage:
        hits = [s for s in self.stages if s.id == sid or s.id.startswith(sid)]
        if not hits:
            raise SystemExit(f"Etapa desconocida: {sid}. Disponibles: {', '.join(s.id for s in self.stages)}")
        return hits[0]

    def feedback_file(self, stage: Stage) -> Path:
        return self.fdir / "work" / f"{stage.id}.feedback.md"

    def bootstrap(self) -> bool:
        """S00-S02: extrae el IR, deriva el manifiesto y genera bus/simuladores/compose/esqueleto del frontend."""
        self.run(until="S02-scaffold")
        return all(self.state.get(i, {}).get("status") == "passed" for i in ("S00-ir", "S01-manifest", "S02-scaffold"))

    def prepare(self, stage: Stage) -> Path:
        fb = self.feedback_file(stage)
        return self.render(stage, fb.read_text(encoding="utf-8") if fb.exists() else "")

    def next_action(self) -> dict:
        """Qué debe hacer ahora el orquestador-agente. Salida pensada para leerse por Bash como JSON."""
        if self.state.get("S02-scaffold", {}).get("status") != "passed" or not (self.fdir / "manifest.json").exists():
            return {"action": "bootstrap", "command": "python -m forge bootstrap"}
        failed: set[str] = set()
        ready: list[Stage] = []
        for s in self.stages:
            if s.kind == "det":
                continue
            st = self.state.get(s.id, {})
            status = st.get("status", "pending")
            if status == "passed" or self.auto_skip(s):
                continue
            if status in ("failed", "skipped"):
                failed.add(s.id)
                continue
            blockers = [d for d in s.deps if d in failed]
            if blockers:
                self.state[s.id] = {"status": "skipped", "attempts": 0, "reason": f"depende de {blockers}"}
                self.save()
                failed.add(s.id)
                continue
            if all(self.state.get(d, {}).get("status") == "passed" for d in s.deps):
                ready.append(s)
        if ready:
            out = []
            for s in ready:
                n = self.state.get(s.id, {}).get("attempts", 0)
                work = self.prepare(s)
                out.append({"id": s.id, "title": s.title, "agent": agent_for(s.id, self.domain.language), "attempt": n + 1,
                            "max_attempts": s.attempts or self.cfg.agent.max_attempts,
                            "work_order": str(work.relative_to(self.cfg.root)), "retry": n > 0})
            return {"action": "delegate", "stages": out}
        if self.state.get("S60-report", {}).get("status") not in ("passed", "failed"):
            return {"action": "report", "command": "python -m forge report"}
        return {"action": "done", "failed": sorted(failed)}

    def check(self, stage: Stage, record: bool = True) -> bool:
        """Puerta OFICIAL de una etapa con agente. record=False solo informa (autoverificación del subagente)."""
        self.ensure_repo()
        t0 = time.time()
        try:
            results = stage.gates(self.cfg, self.manifest) if stage.gates else []
        except Exception as e:  # noqa: BLE001
            results = [G.Gate(False, "excepción en la puerta", f"{type(e).__name__}: {e}")]
        bad = [g for g in results if not g.ok]
        for g in results:
            first = g.detail.strip().splitlines()[0][:150] if (not g.ok and g.detail.strip()) else ""
            print(f"{'✅' if g.ok else '❌'} {g.name}" + (f": {first}" if first else ""))
        feedback = "\n\n".join(f"### Puerta fallida: {g.name}\n{g.detail.strip()}" for g in bad)[:9000]
        if not record:
            if bad:
                print("\n--- detalle ---\n" + feedback[:4000])
            return not bad
        st = self.state.setdefault(stage.id, {"status": "pending", "attempts": 0})
        st["attempts"] = st.get("attempts", 0) + 1
        mx = stage.attempts or self.cfg.agent.max_attempts
        if not bad:
            st.update(status="passed", ended=datetime.now().isoformat(timespec="seconds"), seconds=round(time.time() - t0))
            st.pop("last_error", None)
            self.feedback_file(stage).unlink(missing_ok=True)
        else:
            st.update(status="failed" if st["attempts"] >= mx else "retry", last_error=feedback[:3000])
            self.feedback_file(stage).write_text(feedback, encoding="utf-8")
            print(f"\n(intento {st['attempts']}/{mx}; realimentación guardada en {self.feedback_file(stage).relative_to(self.cfg.root)})")
        self.save()
        self.commit(stage)
        return not bad

    def render_all(self) -> list[Path]:
        """Renderiza las órdenes de trabajo de todas las etapas con agente (sin ejecutarlas) para inspeccionarlas."""
        for sid in ("S00-ir", "S01-manifest"):
            self.det(next(s for s in self.stages if s.id == sid))
        out = []
        for s in self.stages:
            if s.kind == "agent" and not (s.skip_if and s.skip_if(self.cfg, self.manifest)):
                out.append(self.render(s, ""))
        return out

    def report(self) -> bool:
        self.log("=== Resumen ===")
        ok = True
        for s in self.stages:
            st = self.state.get(s.id, {"status": "pending"})
            icon = {"passed": "✅", "failed": "❌", "skipped": "⏭", "pending": "·", "running": "…"}[st["status"]]
            ok &= st["status"] == "passed"
            self.log(f"  {icon} {s.id:24} {st['status']:8} intentos={st.get('attempts', 0)} {st.get('seconds', '')}")
        return ok
