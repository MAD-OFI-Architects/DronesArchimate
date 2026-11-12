"""Detección de cambios en los insumos de un dominio (modelo ArchiMate y decisiones del arquitecto).

Al construir, el runner compara la huella actual con la de la última construcción. Si el modelo o las decisiones
cambiaron, reabre las etapas afectadas; así `build` reconstruye lo que corresponde sin pasar `--force` a mano.
Dos huellas, para reabrir solo lo necesario:
  · modelo  → lo que define qué se construye (símbolos esperados + lenguaje, arquitectura, estilo, BD, puerto, patrones).
  · justificaciones → el texto que el arquitecto escribe por decisión; solo afecta a la memoria de decisiones.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

from .archimate import build_ir
from .config import Config, Domain
from .manifest import build_manifest

ARCHIVO = "insumos.json"
ETAPAS_DE_JUSTIFICACIONES = ("S03-adr", "S50-verify", "S60-report")


def _sha(valor: object) -> str:
    return hashlib.sha256(json.dumps(valor, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def huellas(cfg: Config, d: Domain) -> dict:
    manifiesto = build_manifest(build_ir(cfg.archimate, cfg.docs_dir), [d], cfg.con_frontend)
    decision = {k: v for k, v in dataclasses.asdict(d).items() if k != "rationale"}
    return {
        "modelo": _sha({"manifiesto": manifiesto, "decision": decision}),
        "justificaciones": _sha(d.rationale),
        "simbolos": sorted(f"{i['kind']}:{i['name']}" for i in manifiesto["items"]),
    }


def leer(carpeta: Path) -> dict | None:
    archivo = carpeta / ARCHIVO
    try:
        return json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else None
    except (OSError, ValueError):
        return None


def guardar(carpeta: Path, actual: dict) -> None:
    (carpeta / ARCHIVO).write_text(json.dumps(actual, indent=2, ensure_ascii=False), encoding="utf-8")


def diferencia(previa: dict, actual: dict) -> dict:
    """Qué cambió respecto de la última construcción: `modelo`/`justificaciones` y los símbolos añadidos/quitados."""
    antes, ahora = set(previa.get("simbolos", [])), set(actual["simbolos"])
    return {
        "modelo": previa.get("modelo") != actual["modelo"],
        "justificaciones": previa.get("justificaciones") != actual["justificaciones"],
        "agregados": sorted(ahora - antes),
        "quitados": sorted(antes - ahora),
    }


def pendiente(cfg: Config, d: Domain, carpeta: Path) -> str:
    """'' si está al día (o no hay base con qué comparar); si no, qué cambió: 'modelo' o 'justificaciones'."""
    previa = leer(carpeta)
    if previa is None:
        return ""
    try:
        cambio = diferencia(previa, huellas(cfg, d))
    except Exception:  # noqa: BLE001 — un modelo ilegible lo reporta la etapa S00, no esta consulta
        return ""
    return "modelo" if cambio["modelo"] else ("justificaciones" if cambio["justificaciones"] else "")
