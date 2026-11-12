"""Servicio de la TUI: todo lo que la interfaz necesita, sin una sola línea de Textual (así se prueba sin terminal).

Reutiliza el generador tal cual (`decisions`, `advisor`, `Runner`, `cmd_assemble`): la TUI es solo presentación.
"""
from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

from .. import cli, contextinfo, decisions
from ..archimate import build_ir
from ..config import Config, Domain
from ..credentials import CredentialStore
from ..stages import build_stages

Sink = Callable[[str], None]
CATEGORY_ORDER = ("creacional", "estructural", "comportamiento", "dominio", "aplicación", "persistencia", "integración", "resiliencia", "infraestructura")


class StudioError(ValueError):
    """Decisión o acción inválida; el mensaje se muestra al usuario tal cual."""


@dataclass
class DomainRow:
    context: str
    classification: str
    aggregates: int
    commands: int
    domain: Domain | None
    status: str

    @property
    def decided(self) -> bool:
        return self.domain is not None


@dataclass
class StageRow:
    id: str
    title: str
    status: str          # pending | running | passed | failed | skipped
    attempts: int = 0
    seconds: int = 0
    error: str = ""


class _Lines(io.TextIOBase):
    """Convierte lo que `print` escribe en líneas para un sink."""
    def __init__(self, sink: Sink):
        self.sink, self.buf = sink, ""

    def writable(self) -> bool:
        return True

    def write(self, s: str) -> int:
        self.buf += s
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            self.sink(line)
        return len(s)

    def flush_rest(self) -> None:
        if self.buf:
            self.sink(self.buf)
            self.buf = ""


@dataclass
class BuildHandle:
    threads: dict[str, threading.Thread] = field(default_factory=dict)
    results: dict[str, int] = field(default_factory=dict)
    cancel_event: threading.Event = field(default_factory=threading.Event)

    @property
    def running(self) -> bool:
        return any(t.is_alive() for t in self.threads.values())

    def cancel(self) -> None:
        self.cancel_event.set()

    def wait(self, timeout: float | None = None) -> None:
        for t in self.threads.values():
            t.join(timeout)


class Studio:
    def __init__(self, cfg: Config, creds: CredentialStore | None = None):
        self.cfg = cfg
        self.creds = creds or CredentialStore()
        self._ir: dict | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------- modelo y dominios
    @property
    def ir(self) -> dict:
        if self._ir is None:
            self._ir = build_ir(self.cfg.archimate, self.cfg.docs_dir)
        return self._ir

    def reload(self) -> None:
        self._ir = None
        self.cfg.domains = decisions.load_all(self.cfg)

    def status_of(self, d: Domain) -> str:
        return cli._domain_status(self.cfg, d)

    def rows(self) -> list[DomainRow]:
        decided = {d.context: d for d in self.cfg.domains}
        aggs = {a["name"]: a for a in self.ir["aggregates"]}
        rows = []
        for c in self.ir["contexts"]:
            own = {n for n in c["aggregates"] if n in aggs}
            ncmd = sum(1 for x in self.ir["commands"] if x["aggregate"] in own)
            d = decided.get(c["name"])
            rows.append(DomainRow(c["name"], c.get("classification", ""), len(own), ncmd, d, self.status_of(d) if d else "se simula"))
        return rows

    # ------------------------------------------------------------- decisiones
    def catalog(self) -> dict:
        return decisions.catalog(self.cfg.tool_root)

    def reference(self) -> list[dict]:
        """Fichas informativas de los patrones del catálogo (en el orden del catálogo). Solo describen: no recomiendan ni preseleccionan."""
        items = [{"id": pid, **spec} for pid, spec in self.catalog().items()]
        rank = {c: i for i, c in enumerate(CATEGORY_ORDER)}
        return sorted(items, key=lambda a: rank.get(a.get("categoria", ""), len(rank)))      # estable: dentro de cada categoría, el orden del catálogo

    def facts(self, context: str) -> dict:
        return contextinfo.facts(self.ir, context)

    def draft(self, context: str) -> Domain:
        """La decisión guardada o, si no hay, un formulario EN BLANCO: ningún lenguaje, arquitectura, estilo, base de datos ni patrón
        viene elegido. El arquitecto decide todo."""
        cur = next((d for d in self.cfg.domains if d.context == context), None)
        if cur:
            return dataclasses.replace(cur, patterns={k: dict(v) for k, v in cur.patterns.items()}, rationale=dict(cur.rationale))
        used = {d.port for d in self.cfg.domains}
        port = next(p for p in range(5101, 5300) if p not in used)
        return Domain(context, "", "", "", "", port, patterns={pid: {"usar": False} for pid in self.catalog()})

    def check(self, d: Domain) -> tuple[list[str], list[str]]:
        from .. import gates as G
        missing = [n for n, v in (("el lenguaje", d.language), ("la arquitectura interna", d.architecture), ("el estilo de servicio", d.style),
                                  ("la base de datos", d.database)) if not v]
        if missing:
            return [f"Elige {n}." for n in missing], []
        errors, warns = decisions.validate(self.cfg, d)
        if self.cfg.policy.get("require_justifications"):
            for k in ("lenguaje", "arquitectura", "estilo", "base_de_datos"):
                if d.rationale.get(k) and G.weak_argument(d.rationale[k]):      # la que falta del todo ya la avisa decisions.validate
                    warns.append(f"La justificación de «{k}» es un borrador o es muy corta (mín. {G.MIN_ARGUMENT} caracteres): la política del proyecto la rechaza.")
        return errors, warns

    def save(self, d: Domain) -> Path:
        errors, _ = self.check(d)
        if errors:
            raise StudioError("\n".join(errors))
        p = decisions.write(self.cfg, d)
        self.reload()
        return p

    def save_platform(self, elecciones: dict, why: dict | None = None, imagenes: dict | None = None) -> Path:
        try:
            p = decisions.write_platform(self.cfg, elecciones, why, imagenes)
        except SystemExit as e:
            raise StudioError(str(e)) from e
        self.reload()
        return p

    def policy_findings(self) -> list[str]:
        """Estado de las políticas que el equipo declaró en forge.toml. Vacío si el proyecto no declara ninguna."""
        from .. import gates as G
        names = [c["name"] for c in self.ir["contexts"]]
        out = []
        for g in G.policy_gates(self.cfg, self.cfg.domains, names):
            name = g.name.removeprefix("política: ")
            out.append(f"✓ {name}" if g.ok else f"✗ {name}: {g.detail.splitlines()[0] if g.detail else ''}")
        return out

    # ------------------------------------------------------------- herramientas y agente
    def tool_checks(self, domains: list[Domain] | None = None):
        return cli.tool_checks(self.cfg, domains)

    def agent_env(self) -> dict[str, str]:
        return self.creds.env()

    # ------------------------------------------------------------- construcción
    def progress(self, d: Domain) -> list[StageRow]:
        c = self.cfg.for_domain(d)
        sf = self.cfg.root / c.state_dir / "state.json"
        st = json.loads(sf.read_text(encoding="utf-8")) if sf.exists() else {}
        return [StageRow(s.id, s.title, st.get(s.id, {}).get("status", "pending"), st.get(s.id, {}).get("attempts", 0),
                         st.get(s.id, {}).get("seconds", 0), st.get(s.id, {}).get("last_error", ""))
                for s in build_stages(c)]

    def start_build(self, domains: list[Domain], sink: Sink, *, laps: int = 1, wait: int = 60, only: str | None = None,
                    from_: str | None = None, until: str | None = None, force: bool = False,
                    skip_permissions: bool = False) -> BuildHandle:
        if not domains:
            raise StudioError("Elige al menos un dominio para construir.")
        h = BuildHandle()
        args = SimpleNamespace(laps=laps, wait=wait, only=only, from_=from_, until=until, force=force, skip_permissions=skip_permissions)
        env = self.agent_env()

        def work(d: Domain) -> None:
            tag = lambda line, d=d: sink(f"[{d.slug}] {line}")  # noqa: E731
            try:
                h.results[d.slug] = cli.build_one(self.cfg, d, args, sink=tag, agent_env=env, cancel=h.cancel_event)
            except BaseException as e:  # noqa: BLE001 — un fallo de un dominio no debe tumbar a los demás ni a la TUI
                tag(f"❌ error inesperado: {type(e).__name__}: {e}")
                h.results[d.slug] = 1

        for d in domains:
            h.threads[d.slug] = threading.Thread(target=work, args=(d,), daemon=True, name=f"build-{d.slug}")
        for t in h.threads.values():
            t.start()
        return h

    def assemble(self, sink: Sink) -> int:
        """Une los dominios construidos y corre el humo completo. Captura lo que imprime `forge assemble`."""
        lines = _Lines(sink)
        try:
            with self._lock, contextlib.redirect_stdout(lines):
                return cli.cmd_assemble(self.cfg, None)
        except SystemExit as e:
            sink(f"❌ {e}")
            return 1
        finally:
            lines.flush_rest()
