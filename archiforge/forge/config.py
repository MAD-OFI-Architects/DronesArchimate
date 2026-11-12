"""Configuración del pipeline (forge.toml) y dominios decididos por el arquitecto (decisiones/<dominio>.toml)."""
from __future__ import annotations

import dataclasses
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .util import kebab, pascal

# capa -> fragmentos de ruta (minúsculas) donde debe DECLARARSE el símbolo. Es la unión de las dos arquitecturas soportadas
# (clean-ddd: infrastructure/api · hexagonal: adapters/outbound/inbound) para que el lenguaje y la arquitectura sean independientes.
_COMMON = {"domain": ["/domain/", ".domain/"], "application": ["/application/", ".application/"],
           "contracts": ["/contracts/", ".contracts/"],
           "infrastructure": ["/infrastructure/", ".infrastructure/", "/adapters/outbound/", ".adapters.outbound/", "/adapters/outbound."],
           "api": ["/api/", ".api/", "/adapters/inbound/", ".adapters.inbound/", "/adapters/inbound."],
           "tests": ["/tests/", ".tests/", "tests/", "/src/test/"]}
LAYERS_BY_LANG = {"csharp": _COMMON, "python": _COMMON, "java": _COMMON}
LANGUAGES = ("csharp", "python", "java")
TOOL_ROOT = Path(__file__).resolve().parent.parent      # donde viven catalog/, prompts/, reference/ y config/ (la herramienta)


@dataclass
class Domain:
    context: str
    language: str                  # csharp | python | java
    architecture: str = "clean-ddd"      # clean-ddd | hexagonal
    style: str = "microservicio"         # microservicio | soa | monolito-modular
    database: str = "postgresql"         # mongodb | postgresql
    port: int = 5101
    patterns: dict = field(default_factory=dict)     # id -> {"usar": bool, ...detalle}
    rationale: dict = field(default_factory=dict)    # decisión -> justificación del arquitecto
    slug: str = ""
    prefix: str = ""                     # prefijo PascalCase de proyectos/paquetes

    def __post_init__(self):
        self.slug = self.slug or kebab(self.context)
        self.prefix = self.prefix or pascal(self.context)

    @property
    def dir(self) -> str:
        return f"services/{self.slug}"

    def uses(self, pattern: str) -> bool:
        p = self.patterns.get(pattern)
        return bool(p and p.get("usar", True))


@dataclass
class AgentCfg:
    engine: str = "claude"            # claude | opencode | custom
    model: str = ""                   # opencode: "proveedor/modelo" (p. ej. opencode/deepseek-v4.1-flash-free)
    opencode_agent: str = ""          # agente OpenCode por defecto; el pipeline usa el forge-* de cada etapa
    max_attempts: int = 3
    timeout_minutes: int = 90
    extra_args: list[str] = field(default_factory=list)
    custom_argv: list[str] = field(default_factory=list)   # {prompt_file} {prompt} {workdir}


@dataclass
class Config:
    root: Path                        # raíz del PROYECTO: forge.toml, decisiones/, .forge/ y out/
    archimate: Path
    docs_dir: Path | None             # documentos de fase (opcional: sin ellos el contexto de cada agregado puede faltar)
    guide: Path
    out: Path
    domains: list[Domain]
    agent: AgentCfg
    min_conformance: float = 0.9
    strict_tools: bool = True
    state_dir: str = ".forge"
    repo: str = ""                    # URL del repositorio del producto (se clona en out/ si no existe)
    decisions_dir: Path = Path("decisiones")
    raw: dict = field(default_factory=dict)
    policy: dict = field(default_factory=dict)     # [policy] de forge.toml: reglas opcionales del equipo (sin sección, no se exige nada)
    platform: dict = field(default_factory=dict)   # decisiones de la plataforma (decisiones/plataforma.toml): p. ej. el canal de eventos
    tool_root: Path = TOOL_ROOT       # raíz de la HERRAMIENTA; distinta de `root` cuando el proyecto vive aparte (TUI)

    def for_domain(self, d: Domain) -> "Config":
        """Vista de la configuración para construir UN dominio: estado propio y solo ese dominio."""
        return dataclasses.replace(self, domains=[d], state_dir=f"{self.state_dir}/{d.slug}")


def _resolve(root: Path, rel: str) -> Path:
    """Recurso de referencia: el del proyecto si existe; si no, el de la herramienta."""
    own = root / rel
    return own if own.exists() else TOOL_ROOT / rel


def load(path: Path) -> Config:
    from . import decisions
    path = Path(path).resolve()
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    root = path.parent
    inp, out = raw["inputs"], raw.get("output", {})
    from . import personal
    ag = {**raw.get("agent", {}), **personal.load(path)}      # lo personal gana sobre el valor del equipo (forge.toml)
    cfg = Config(
        root=root,
        archimate=root / inp["archimate"],
        docs_dir=(root / inp["docs_dir"]) if inp.get("docs_dir") else None,
        guide=_resolve(root, inp.get("reference_guide", "reference/guia_ddd.md")),
        out=root / out.get("dir", "out"),
        domains=[],
        agent=AgentCfg(**ag),
        min_conformance=raw.get("quality", {}).get("min_conformance", 0.9),
        strict_tools=raw.get("quality", {}).get("strict_tools", True),
        state_dir=out.get("state_dir", ".forge"),
        repo=out.get("repo", ""),
        decisions_dir=root / raw.get("decisions", {}).get("dir", "decisiones"),
        raw=raw,
        policy=dict(raw.get("policy", {})),
    )
    cfg.domains = decisions.load_all(cfg)
    cfg.platform = decisions.read_platform(cfg)
    return cfg
