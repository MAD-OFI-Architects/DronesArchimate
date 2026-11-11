"""Proyectos de la TUI: una carpeta por proyecto con su `forge.toml` GENERADO (el usuario no escribe configuración).

Un proyecto = un `.archimate` + decisiones por dominio + estado + producto generado (`out/`). La herramienta (catalog, prompts…)
vive aparte (`Config.tool_root`). El registro de proyectos y los tokens viven en el directorio de configuración del usuario.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .. import agentdefs, config
from ..config import TOOL_ROOT, Config
from ..credentials import default_path as _cred_path
from ..util import kebab

ENGINES = ("opencode", "claude", "custom")


class ProjectError(ValueError):
    """Entrada inválida del usuario (mensaje apto para mostrar tal cual)."""


@dataclass(frozen=True)
class AgentSettings:
    engine: str = "opencode"            # opencode | claude | custom
    model: str = ""                     # opencode: proveedor/modelo · claude: alias o id del modelo
    opencode_agent: str = ""
    max_attempts: int = 3
    timeout_minutes: int = 90
    custom_argv: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if self.engine not in ENGINES:
            raise ProjectError(f"Motor de agente «{self.engine}» no soportado (usa: {', '.join(ENGINES)}).")
        if self.engine == "custom" and not self.custom_argv:
            raise ProjectError("El motor «custom» necesita el comando a ejecutar (usa {prompt_file} donde va la orden de trabajo).")
        if self.max_attempts < 1 or self.timeout_minutes < 1:
            raise ProjectError("Intentos y tiempo máximo deben ser al menos 1.")

    @classmethod
    def from_cfg(cls, a: config.AgentCfg) -> "AgentSettings":
        return cls(a.engine, a.model, a.opencode_agent, a.max_attempts, a.timeout_minutes, tuple(a.custom_argv))


def _q(v: str) -> str:
    return json.dumps(v, ensure_ascii=False)


def agent_block(a: AgentSettings) -> str:
    L = ["[agent]", f"engine = {_q(a.engine)}"]
    if a.model:
        L.append(f"model = {_q(a.model)}")
    if a.opencode_agent:
        L.append(f"opencode_agent = {_q(a.opencode_agent)}")
    L += [f"max_attempts = {a.max_attempts}", f"timeout_minutes = {a.timeout_minutes}"]
    if a.custom_argv:
        L.append("custom_argv = [" + ", ".join(_q(x) for x in a.custom_argv) + "]")
    return "\n".join(L) + "\n"


_SECTION = re.compile(r"^\[agent\][^\n]*\n(?:(?!\[)[^\n]*\n?)*", re.M)


def set_agent_block(toml_text: str, a: AgentSettings) -> str:
    """Reemplaza solo la sección [agent] (conserva el resto y sus comentarios); si no existe, la añade."""
    block = agent_block(a)
    if _SECTION.search(toml_text):
        return _SECTION.sub(lambda _m: block, toml_text, count=1)
    return toml_text.rstrip("\n") + "\n\n" + block


def render_forge_toml(archimate: Path, docs_dir: Path | None, agent: AgentSettings) -> str:
    L = ["# Generado por la TUI de ArchiForge. Se puede editar a mano, pero no hace falta.", "[inputs]", f"archimate = {_q(str(archimate))}"]
    if docs_dir:
        L.append(f"docs_dir = {_q(str(docs_dir))}")
    L += ["", "[output]", 'dir = "out"', "", "[decisions]", 'dir = "decisiones"', "",
          "[quality]", "min_conformance = 0.9", "strict_tools = true", "skip = []", ""]
    return "\n".join(L) + "\n" + agent_block(agent)


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    slug: str
    toml: Path

    @property
    def root(self) -> Path:
        return self.toml.parent


def default_registry() -> Path:
    return _cred_path().parent / "projects.json"


class ProjectStore:
    def __init__(self, registry: Path | None = None, home: Path | None = None):
        self.registry = Path(registry) if registry else default_registry()
        self.home = Path(home) if home else TOOL_ROOT / "projects"

    def _read(self) -> list[dict]:
        if not self.registry.exists():
            return []
        try:
            data = json.loads(self.registry.read_text(encoding="utf-8"))
            return [x for x in data if isinstance(x, dict) and {"name", "toml"} <= x.keys()]
        except (OSError, ValueError):
            return []

    def _write(self, items: list[dict]) -> None:
        self.registry.parent.mkdir(parents=True, exist_ok=True)
        self.registry.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    def list(self) -> list[ProjectInfo]:
        out = []
        for x in self._read():
            t = Path(x["toml"])
            if t.exists():
                out.append(ProjectInfo(x["name"], kebab(x["name"]), t))
        return out

    def register(self, toml: Path, name: str | None = None) -> ProjectInfo:
        toml = Path(toml).resolve()
        if not toml.exists():
            raise ProjectError(f"No existe {toml}.")
        name = (name or toml.parent.name).strip()
        items = [x for x in self._read() if Path(x["toml"]).resolve() != toml]
        items.append({"name": name, "toml": str(toml)})
        self._write(items)
        return ProjectInfo(name, kebab(name), toml)

    def forget(self, info: ProjectInfo) -> None:
        """Quita el proyecto del registro. NUNCA borra archivos."""
        self._write([x for x in self._read() if Path(x["toml"]).resolve() != info.toml.resolve()])

    def create(self, name: str, archimate: Path, docs_dir: Path | None, agent: AgentSettings) -> ProjectInfo:
        name = name.strip()
        slug = kebab(name)
        if not slug:
            raise ProjectError("Ponle un nombre al proyecto.")
        archimate = Path(archimate).expanduser().resolve()
        if not archimate.is_file() or archimate.suffix.lower() != ".archimate":
            raise ProjectError(f"«{archimate}» no es un archivo .archimate.")
        if docs_dir:
            docs_dir = Path(docs_dir).expanduser().resolve()
            if not docs_dir.is_dir():
                raise ProjectError(f"La carpeta de documentos «{docs_dir}» no existe.")
        agent.validate()
        root = self.home / slug
        if (root / "forge.toml").exists():
            raise ProjectError(f"Ya existe un proyecto «{slug}» en {root}.")
        (root / "decisiones").mkdir(parents=True, exist_ok=True)
        (root / "forge.toml").write_text(render_forge_toml(archimate, docs_dir, agent), encoding="utf-8")
        for f in ("AGENTS.md", "CLAUDE.md"):                     # las órdenes de trabajo dicen al agente qué puede tocar
            if (TOOL_ROOT / f).exists():
                shutil.copy(TOOL_ROOT / f, root / f)
        agentdefs.install(root, ("claude", "opencode"), agent.model)
        return self.register(root / "forge.toml", name)

    def load(self, info: ProjectInfo) -> Config:
        return config.load(info.toml)

    def save_agent(self, info: ProjectInfo, agent: AgentSettings) -> None:
        """Guarda motor/modelo del proyecto y regenera sus agentes (el modelo va dentro de la definición de cada agente)."""
        agent.validate()
        text = info.toml.read_text(encoding="utf-8")
        info.toml.write_text(set_agent_block(text, agent), encoding="utf-8")
        agentdefs.install(info.root, ("claude", "opencode"), agent.model)
