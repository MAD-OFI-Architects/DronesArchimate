"""Definición de las etapas de UN dominio: qué hace cada una, de quién depende y qué puertas debe pasar.

La forma del pipeline sale de las decisiones del arquitecto (arquitectura → hay o no kernel; patrones → qué se exige).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

from . import gates as G
from .config import Config


@dataclass
class Stage:
    id: str
    title: str
    kind: str                                   # det | agent
    deps: list[str] = field(default_factory=list)
    template: str = ""                          # prompts/<template>
    params: dict = field(default_factory=dict)
    scope: list[str] = field(default_factory=list)          # rutas donde el agente puede escribir
    gates: Callable[[Config, dict], list[G.Gate]] | None = None   # (cfg, manifest) -> resultados
    gates_text: str = ""
    attempts: int | None = None
    always: bool = False                        # corre aunque fallen sus dependencias (p. ej. el reporte final)
    skip_if: Callable[[Config, dict], str] | None = None    # devuelve el motivo si la etapa no aplica


def _skip_cfg(key: str):
    return lambda c, m: "omitida por configuración (quality.skip)" if key in c.raw.get("quality", {}).get("skip", []) else ""


def build_stages(cfg: Config) -> list[Stage]:
    d = cfg.domains[0]
    sl = d.slug
    ctx = {d.context}
    svc, docs = f"out/services/{sl}/", f"out/docs/{sl}/"
    gt = lambda layers, label: (lambda c, m: G.build_gates(c, d, layers, label))
    S = [
        Stage("S00-ir", "Extraer el modelo ArchiMate a IR", "det"),
        Stage("S01-manifest", "Derivar el manifiesto de símbolos esperados", "det", ["S00-ir"]),
        Stage("S02-scaffold", "Esqueleto del dominio, microfrontend y plataforma de humo", "det", ["S01-manifest"]),
        Stage("S03-adr", "Decisiones de arquitectura argumentadas (ADR)", "agent", ["S02-scaffold"], "adr.md.j2",
              scope=[docs], gates=lambda c, m: [G.adr_gate(c, m, final=False)],
              gates_text=f"`{docs}decisiones-arquitectura.md` con todas las secciones y la tabla de patrones."),
    ]
    pre = "S03-adr"
    if d.architecture == "clean-ddd":
        S.append(Stage("S10-kernel", f"{d.context}: proyecto y shared kernel", "agent", [pre], "kernel.md.j2", {}, [svc],
                       gt(None, ""), "Compila, pasan las pruebas del kernel y se respeta la regla de dependencias."))
        pre = "S10-kernel"
    S += [
        Stage("S11-domain", f"{d.context}: capa de dominio", "agent", [pre], "layer.md.j2",
              {"layer": "domain", "layers": {"domain"}}, [svc, docs], gt({"domain"}, "conformidad: dominio"),
              "Todos los símbolos de dominio declarados; compila y las pruebas pasan; dependencias respetadas."),
        Stage("S12-application", f"{d.context}: aplicación y contratos", "agent", ["S11-domain"], "layer.md.j2",
              {"layer": "application", "layers": {"application", "contracts"}}, [svc, docs],
              gt({"application", "contracts"}, "conformidad: aplicación+contratos"),
              "Símbolos de aplicación/contratos declarados; compila y las pruebas pasan."),
        Stage("S13-adapters", f"{d.context}: adaptadores, API y despliegue", "agent", ["S12-application"], "layer.md.j2",
              {"layer": "adapters", "layers": {"infrastructure", "api", "tests", "ops"}}, [svc, docs],
              gt({"infrastructure", "api", "tests", "ops"}, "conformidad: adaptadores+API+pruebas"),
              "Símbolos de adaptadores/API/pruebas/despliegue declarados; compila y las pruebas pasan."),
        Stage("S30-smoke", "Humo aislado del dominio (bus + simuladores + su servicio)", "agent", ["S13-adapters"], "smoke.md.j2", {},
              [svc, docs],
              lambda c, m: [G.files_gate(c, [f"services/{sl}/smoke/smoke.py", f"docs/{sl}/ejecucion.md"]), G.smoke_domain_gate(c, d)],
              "`docker compose up --wait` de la plataforma de humo del dominio y `smoke/smoke.py` terminan con código 0.",
              skip_if=_skip_cfg("smoke")),
        Stage("S40-microfrontend", f"Microfrontend de {d.context} (Web Component)", "agent", ["S30-smoke"], "mfe.md.j2", {},
              [f"out/frontend/mfe-{sl}/", docs],
              lambda c, m: [G.conformance_gate(c, m, {"frontend"}, None, 1.0, "conformidad: formularios"),
                            G.stubs_gate(c, f"frontend/mfe-{sl}"), G.npm_build(c, f"frontend/mfe-{sl}")],
              "Un `…Form` por comando de usuario sin marcas `FORGE-STUB`, y `npm run build` del remote en verde.",
              skip_if=lambda c, m: _skip_cfg("frontend")(c, m) or ("" if m["frontend"]["remotes"] else "el dominio no tiene comandos de usuario")),
        Stage("S50-verify", "Revisión independiente (decisiones, SOLID, DDD, patrones)", "agent", ["S40-microfrontend"], "verify.md.j2", {},
              [svc, f"out/frontend/mfe-{sl}/", docs],
              lambda c, m: [G.report_gate(c, f"docs/{sl}/verificacion.md", ["veredicto"]), G.adr_gate(c, m, final=True)],
              "`verificacion.md` con tabla de hallazgos y veredicto; el ADR cubre cada patrón elegido y cita solo clases que existen."),
        Stage("S60-report", "Conformidad final y trazabilidad del dominio", "det", ["S50-verify"], always=True),
    ]
    return S


# Subagente nativo (Claude Code / OpenCode) que ejecuta cada etapa con agente.
def agent_for(stage_id: str, language: str = "") -> str:
    if stage_id.startswith("S03"):
        return "forge-architect"
    if stage_id.startswith(("S10", "S11", "S12", "S13")):
        return {"csharp": "forge-csharp", "python": "forge-python", "java": "forge-java"}.get(language, "forge-python")
    if stage_id.startswith("S30"):
        return "forge-integrator"
    if stage_id.startswith("S40"):
        return "forge-frontend"
    return "forge-reviewer"
