"""Adaptadores de agente: Claude Code y OpenCode (y un modo `custom`).

El prompt NUNCA viaja largo por la línea de comandos: el orquestador escribe una orden de trabajo en
`.forge/work/<etapa>.md` y el agente recibe un mensaje corto que le pide leerla. Así funciona igual en
Windows, macOS y Linux (sin límites de longitud ni comillas).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from .config import AgentCfg

CLAUDE_ALLOWED = ("Bash Edit Write Read Glob Grep")   # Bash completo: dotnet, python, npm, docker, git…


def short_message(work_file: Path, root: Path) -> str:
    rel = work_file.relative_to(root).as_posix()
    return (f"Lee el archivo {rel} y ejecuta TODAS sus instrucciones de principio a fin, sin pedir confirmación. "
            f"Trabaja solo dentro de las rutas que la orden indica. Al terminar, resume en 5 líneas lo hecho.")


def build_argv(cfg: AgentCfg, work_file: Path, root: Path, skip_permissions: bool = False,
               agent: str | None = None) -> tuple[list[str], str | None]:
    """Devuelve (argv, stdin). stdin solo se usa si el motor lo requiere.

    OpenCode V2: el directorio lo toma del `cwd` del proceso (no existe `--dir`), `--auto` evita
    las confirmaciones y `--agent` elige el agente. `agent` (por etapa) gana sobre `cfg.opencode_agent`.
    """
    msg = short_message(work_file, root)
    eng = cfg.engine
    if eng == "claude":
        argv = ["claude", "-p", msg, "--output-format", "text"]
        if skip_permissions:
            argv.append("--dangerously-skip-permissions")
        else:
            argv += ["--permission-mode", "acceptEdits", "--allowedTools", CLAUDE_ALLOWED]
        if cfg.model:
            argv += ["--model", cfg.model]
        return argv + cfg.extra_args, None
    if eng == "opencode":
        argv = ["opencode", "run", msg, "--auto"]
        chosen = agent or cfg.opencode_agent
        if chosen:
            argv += ["--agent", chosen]
        if cfg.model:
            argv += ["-m", cfg.model]
        return argv + cfg.extra_args, None
    if eng == "custom":
        sub = {"{prompt_file}": str(work_file), "{prompt}": msg, "{workdir}": str(root)}
        argv = [sub.get(a, a) for a in cfg.custom_argv]
        return argv, None
    raise ValueError(f"Motor de agente desconocido: {eng}")


def write_opencode_config(root: Path) -> None:
    """OpenCode V2 pide permisos por acción; en modo desatendido se permiten edición, shell y red.

    Las reglas del agente (`permissions` en su frontmatter) se añaden DESPUÉS y mandan sobre esto.
    """
    p = root / "opencode.json"
    if not p.exists():
        p.write_text(json.dumps({
            "$schema": "https://opencode.ai/config.json",
            "permissions": [
                {"action": "edit", "resource": "*", "effect": "allow"},
                {"action": "shell", "resource": "*", "effect": "allow"},
                {"action": "webfetch", "resource": "*", "effect": "allow"},
            ],
        }, indent=2), encoding="utf-8")


def run_agent(cfg: AgentCfg, work_file: Path, root: Path, log_file: Path, skip_permissions: bool = False,
              agent: str | None = None) -> tuple[bool, str]:
    argv, stdin = build_argv(cfg, work_file, root, skip_permissions, agent)
    exe = shutil.which(argv[0])
    if not exe:
        return False, f"No se encontró el ejecutable '{argv[0]}' en el PATH."
    argv[0] = exe
    if cfg.engine == "opencode":
        write_opencode_config(root)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        with log_file.open("w", encoding="utf-8", errors="replace") as fh:
            fh.write(f"$ {' '.join(argv[:3])} …\n\n")
            fh.flush()
            proc = subprocess.run(argv, cwd=root, input=stdin, stdin=None if stdin else subprocess.DEVNULL, stdout=fh,
                                  stderr=subprocess.STDOUT, text=True, timeout=cfg.timeout_minutes * 60)
        return proc.returncode == 0, f"código de salida {proc.returncode} en {time.time() - t0:.0f}s"
    except subprocess.TimeoutExpired:
        return False, f"agotó el tiempo ({cfg.timeout_minutes} min)"
    except OSError as e:
        return False, f"no se pudo ejecutar el agente: {e}"
