"""Preferencias PERSONALES de un proyecto: motor y modelo del agente, intentos y tiempo.

Qué va a git y qué no:
- Del EQUIPO (en el repositorio): `forge.toml` (valores por defecto) y `decisiones/*.toml` (las decisiones de arquitectura).
- PERSONAL (nunca en el repositorio): esto y los tokens. Viven en el directorio de configuración del usuario
  (`$XDG_CONFIG_HOME/archiforge/projects/<proyecto>.json`) y `Config.load` los aplica ENCIMA de `forge.toml`.
Así cada persona usa su propio motor, modelo y suscripción sin que sus cambios viajen con el `git push`.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .credentials import default_path

KEYS = ("engine", "model", "opencode_agent", "max_attempts", "timeout_minutes", "custom_argv")


def _key(toml: Path) -> str:
    toml = Path(toml).resolve()
    return f"{toml.parent.name}-{hashlib.sha1(str(toml).encode()).hexdigest()[:8]}"


def path(toml: Path) -> Path:
    return default_path().parent / "projects" / f"{_key(toml)}.json"


def load(toml: Path) -> dict:
    """El override personal del proyecto, o {}. Un archivo roto se ignora: nunca debe impedir usar el CLI."""
    try:
        data = json.loads(path(toml).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: data[k] for k in KEYS if isinstance(data, dict) and k in data}


def save(toml: Path, data: dict) -> None:
    p = path(toml)
    p.parent.mkdir(parents=True, exist_ok=True)
    clean = {k: data[k] for k in KEYS if k in data}
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".pref-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(clean, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def clear(toml: Path) -> None:
    path(toml).unlink(missing_ok=True)
