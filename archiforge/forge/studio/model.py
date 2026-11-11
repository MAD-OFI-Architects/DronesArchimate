"""Inspección de un .archimate: ¿sirve para generar software? Responde con un veredicto legible, nunca con un traceback."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from ..archimate import build_ir, validate_ir


@dataclass
class ContextSummary:
    name: str
    classification: str
    aggregates: int
    commands: int
    published: int
    consumed: int


@dataclass
class ModelReport:
    path: Path
    contexts: list[ContextSummary] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.contexts) and not self.errors

    @property
    def totals(self) -> dict[str, int]:
        return {"contextos": len(self.contexts), "agregados": sum(c.aggregates for c in self.contexts),
                "comandos": sum(c.commands for c in self.contexts)}


def inspect_model(archimate: Path, docs_dir: Path | None = None) -> ModelReport:
    r = ModelReport(Path(archimate))
    if not r.path.is_file():
        r.errors.append(f"No existe el archivo {r.path}.")
        return r
    if r.path.suffix.lower() != ".archimate":
        r.errors.append("El archivo no termina en .archimate (exporta el modelo desde Archi con «Guardar»).")
        return r
    try:
        ET.parse(r.path)
    except ET.ParseError as e:
        r.errors.append(f"El archivo no es un modelo de Archi válido (XML roto): {e}.")
        return r
    try:
        ir = build_ir(r.path, docs_dir)
    except Exception as e:  # noqa: BLE001 — un modelo ajeno puede romper el parser de muchas formas: se informa, no se propaga
        r.errors.append(f"El generador no pudo interpretar este modelo ({type(e).__name__}: {e}). "
                        "Espera las convenciones de modelado de ArchiForge (agregados con rol Raíz, «Dominio: …», comandos y eventos).")
        return r
    aggs = {a["name"]: a for a in ir["aggregates"]}
    for c in ir["contexts"]:
        own = [aggs[n] for n in c["aggregates"] if n in aggs]
        cmds = [x for x in ir["commands"] if x["aggregate"] in {a["name"] for a in own}]
        r.contexts.append(ContextSummary(c["name"], c.get("classification", ""), len(own), len(cmds),
                                         len(c.get("published_events", [])), len(c.get("consumed_events", []))))
    r.errors, r.warnings = validate_ir(ir)
    if not r.contexts:
        r.errors.append("El modelo no define contextos delimitados (carpetas o grupos «Dominio: …»).")
    if docs_dir is None and any("sin contexto" in e for e in r.errors):
        r.hints.append("En este modelo el mapa de contextos y los contratos vienen de los documentos de fase "
                       "(Fase05/01_mapa_de_contextos.md, Fase02/04_contratos_servicios.md): indica la carpeta de documentos.")
    return r
