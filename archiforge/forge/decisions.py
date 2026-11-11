"""Decisiones del arquitecto: un archivo por dominio (decisiones/<dominio>.toml). La herramienta recomienda; aquí se decide."""
from __future__ import annotations

import tomllib
from pathlib import Path

from .config import LANGUAGES, Config, Domain
from .util import kebab, norm

ARCHITECTURES = ("clean-ddd", "hexagonal")
STYLES = ("microservicio", "soa", "monolito-modular")
DATABASES = ("mongodb", "postgresql")
DECISION_KEYS = ("lenguaje", "arquitectura", "estilo", "base_de_datos")


def catalog(root: Path) -> dict[str, dict]:
    return tomllib.loads((root / "catalog" / "patrones.toml").read_text(encoding="utf-8"))


def path_for(cfg: Config, slug: str) -> Path:
    return cfg.decisions_dir / f"{slug}.toml"


def _norm_patterns(raw: dict) -> dict:
    out = {}
    for pid, v in (raw or {}).items():
        if isinstance(v, bool):
            out[pid] = {"usar": v}
        elif isinstance(v, dict):
            out[pid] = {"usar": v.get("usar", True), **{k: x for k, x in v.items() if k != "usar"}}
        else:
            raise SystemExit(f"patrones.{pid}: usa true/false o una tabla ({{ aplicar_en = \"…\" }}).")
    return out


def read(file: Path) -> Domain:
    raw = tomllib.loads(file.read_text(encoding="utf-8"))
    missing = [k for k in ("contexto", *DECISION_KEYS) if k not in raw]
    if missing:
        raise SystemExit(f"{file.name}: faltan decisiones: {', '.join(missing)}. Decide cada una; la herramienta no elige por ti.")
    return Domain(context=raw["contexto"], language=raw["lenguaje"], architecture=raw["arquitectura"], style=raw["estilo"],
                  database=raw["base_de_datos"], port=int(raw.get("puerto", 0)) or 5101,
                  patterns=_norm_patterns(raw.get("patrones")), rationale=dict(raw.get("justificacion", {})))


def load_all(cfg: Config) -> list[Domain]:
    d = cfg.decisions_dir
    out = [read(f) for f in sorted(d.glob("*.toml"))] if d.exists() else []
    seen: dict[int, str] = {}
    for x in out:           # puertos únicos entre dominios decididos
        if x.port in seen:
            x.port = next(p for p in range(5101, 5300) if p not in {y.port for y in out} | set(seen))
        seen[x.port] = x.context
    return out


def find(cfg: Config, name: str) -> Domain | None:
    key = norm(name)
    hits = [d for d in cfg.domains if norm(d.context) == key or d.slug == kebab(name)] or [d for d in cfg.domains if key in norm(d.context)]
    return hits[0] if len(hits) == 1 else None


def validate(cfg: Config, d: Domain) -> tuple[list[str], list[str]]:
    """(errores, avisos). Los errores impiden construir; los avisos informan sin imponer."""
    cat, errors, warns = catalog(cfg.root), [], []
    if d.language not in LANGUAGES:
        errors.append(f"lenguaje «{d.language}» no soportado (usa: {', '.join(LANGUAGES)}).")
    if d.architecture not in ARCHITECTURES:
        errors.append(f"arquitectura «{d.architecture}» no soportada (usa: {', '.join(ARCHITECTURES)}).")
    if d.style not in STYLES:
        errors.append(f"estilo «{d.style}» no soportado (usa: {', '.join(STYLES)}).")
    if d.database not in DATABASES:
        errors.append(f"base de datos «{d.database}» no soportada (usa: {', '.join(DATABASES)}).")
    for pid in d.patterns:
        if pid not in cat:
            errors.append(f"patrón «{pid}» desconocido (catálogo: {', '.join(cat)}).")
    for pid, p in d.patterns.items():
        for req in cat.get(pid, {}).get("requiere", []):
            if p.get("usar") and not d.uses(req):
                errors.append(f"el patrón «{pid}» requiere «{req}» (actívalo o desactiva «{pid}»).")
    for pid, spec in cat.items():
        if spec.get("evaluacion") and not d.uses(pid):
            warns.append(f"La evaluación pide «{spec['nombre']}» y este diseño no lo usa (puede ser intencional; justifícalo en el ADR).")
    for k in ("lenguaje", "base_de_datos", "arquitectura", "estilo"):
        if not d.rationale.get(k):
            warns.append(f"Falta la justificación de «{k}» (el ADR la necesita, y es tu argumento ante el profesor).")
    return errors, warns


def _q(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def write(cfg: Config, d: Domain) -> Path:
    cfg.decisions_dir.mkdir(parents=True, exist_ok=True)
    L = [f"# Decisiones de arquitectura de «{d.context}» — las toma el arquitecto; la herramienta ejecuta fiel a esto.",
         f"contexto = {_q(d.context)}", f"lenguaje = {_q(d.language)}            # {' | '.join(LANGUAGES)}",
         f"arquitectura = {_q(d.architecture)}     # {' | '.join(ARCHITECTURES)}", f"estilo = {_q(d.style)}        # {' | '.join(STYLES)}",
         f"base_de_datos = {_q(d.database)}   # {' | '.join(DATABASES)}", f"puerto = {d.port}", "", "[patrones]   # true = usar · false = descartado"]
    for pid, p in d.patterns.items():
        det = {k: v for k, v in p.items() if k != "usar"}
        if det:
            L.append(f"{pid} = {{ usar = {str(p.get('usar', True)).lower()}, " + ", ".join(f"{k} = {_q(v)}" for k, v in det.items()) + " }")
        else:
            L.append(f"{pid} = {str(p.get('usar', True)).lower()}")
    L += ["", "[justificacion]   # tus razones; el ADR las cita tal cual"]
    for k, v in d.rationale.items():
        L.append(f"{k} = {_q(v)}")
    p = path_for(cfg, d.slug)
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p
