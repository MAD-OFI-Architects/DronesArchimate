"""Tokens de API del usuario, guardados FUERA de cualquier proyecto.

- Viven en el directorio de configuración del usuario (`$XDG_CONFIG_HOME/archiforge/credentials.json`), con permisos 600
  (directorio 700): así no terminan en un repositorio ni en un `forge.toml`.
- Se guardan como pares VARIABLE_DE_ENTORNO -> valor y viajan al agente SOLO por entorno (`agents.run_agent(env=…)`).
- Nunca se imprimen: la interfaz muestra `mask(valor)`.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

# Proveedores habituales -> variable de entorno que leen Claude Code y OpenCode. Orientativo: se puede usar cualquier nombre.
KNOWN = {
    "Anthropic": "ANTHROPIC_API_KEY",
    "OpenAI": "OPENAI_API_KEY",
    "Google Gemini": "GEMINI_API_KEY",
    "OpenRouter": "OPENROUTER_API_KEY",
    "DeepSeek": "DEEPSEEK_API_KEY",
    "Groq": "GROQ_API_KEY",
    "GitHub (Copilot)": "GITHUB_TOKEN",
}


class CredentialError(RuntimeError):
    """El archivo de credenciales existe pero no se puede leer: se informa en vez de vaciarlo en silencio."""


def default_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "archiforge" / "credentials.json"


def mask(value: str) -> str:
    """Forma segura de mostrar un secreto: solo los 4 últimos caracteres y solo si el valor es largo."""
    if not value:
        return ""
    return "•" * max(len(value) - 4, 3) + value[-4:] if len(value) > 8 else "•" * 3


class CredentialStore:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path()

    def _read(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise CredentialError(f"No se pudo leer {self.path}: {e}. Corrígelo o bórralo; no se sobrescribe en silencio.") from e
        if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
            raise CredentialError(f"{self.path} no tiene el formato esperado (VARIABLE: valor).")
        return data

    def _write(self, data: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self.path.parent, 0o700)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".cred-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    def names(self) -> list[str]:
        return sorted(self._read())

    def get(self, name: str) -> str:
        return self._read().get(name, "")

    def env(self) -> dict[str, str]:
        """Variables listas para el entorno del proceso del agente."""
        return dict(self._read())

    def set(self, name: str, value: str) -> None:
        if not NAME.match(name):
            raise ValueError(f"«{name}» no es un nombre de variable válido (MAYÚSCULAS, dígitos y _; p. ej. ANTHROPIC_API_KEY).")
        value = value.strip()
        if not value or "\n" in value or "\r" in value:
            raise ValueError("El token no puede estar vacío ni tener saltos de línea.")
        data = self._read()
        data[name] = value
        self._write(data)

    def delete(self, name: str) -> None:
        data = self._read()
        if data.pop(name, None) is not None:
            self._write(data)
