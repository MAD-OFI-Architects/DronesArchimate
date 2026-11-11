"""Etapa 0: .archimate -> IR (representación intermedia JSON).

El agente NUNCA lee el XML crudo (1,3 MB): trabaja sobre este IR compacto y trazable.
Cada elemento del IR conserva el `id` de ArchiMate para poder demostrar trazabilidad modelo -> código.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from . import mdtables
from .util import pascal

XSI = "{http://www.w3.org/2001/XMLSchema-instance}type"


class Model:
    """Carga plana del .archimate: elementos y relaciones indexados."""

    def __init__(self, path: Path):
        self.path = Path(path)
        root = ET.parse(self.path).getroot()
        self.el: dict[str, dict] = {}
        self.rels: list[dict] = []
        for e in root.iter("element"):
            t = (e.get(XSI) or "").replace("archimate:", "")
            d = {
                "id": e.get("id"),
                "type": t,
                "name": (e.get("name") or "").strip(),
                "doc": (e.findtext("documentation") or "").strip(),
                "props": {p.get("key"): (p.get("value") or "").strip() for p in e.findall("property")},
            }
            if t.endswith("Relationship"):
                d["source"], d["target"] = e.get("source"), e.get("target")
                self.rels.append(d)
            else:
                self.el[d["id"]] = d
        self.out: dict[str, list[dict]] = defaultdict(list)
        self.inn: dict[str, list[dict]] = defaultdict(list)
        for r in self.rels:
            self.out[r["source"]].append(r)
            self.inn[r["target"]].append(r)

    def of_type(self, *types: str) -> list[dict]:
        return [e for e in self.el.values() if e["type"] in types]

    def targets(self, eid: str, rel_type: str) -> list[dict]:
        return [self.el[r["target"]] for r in self.out[eid] if r["type"] == rel_type and r["target"] in self.el]

    def sources(self, eid: str, rel_type: str) -> list[dict]:
        return [self.el[r["source"]] for r in self.inn[eid] if r["type"] == rel_type and r["source"] in self.el]

    def sha(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()[:16]


def _ref(e: dict) -> dict:
    return {"id": e["id"], "name": e["name"]}


def build_ir(archimate: Path, docs_dir: Path | None = None) -> dict:
    m = Model(archimate)
    docs_dir = Path(docs_dir) if docs_dir else None

    # ---- contextos (componentes de aplicación que son contextos delimitados) ----
    contexts: dict[str, dict] = {}
    for c in m.of_type("ApplicationComponent"):
        mt = re.search(r"contexto delimitado «([^»]+)»", c["doc"])
        if mt:
            contexts[c["name"]] = {
                "id": c["id"], "name": c["name"], "classification": c["props"].get("Clasificación", ""),
                "purpose": c["doc"].split(").", 1)[-1].strip() if ")." in c["doc"] else c["doc"],
                "aggregates": [], "services": [], "interfaces": [], "published_events": [], "consumed_events": [],
            }

    # ---- agregados ----
    groupings = {g["id"]: g for g in m.of_type("Grouping")}
    domain_by_name: dict[str, str] = {}
    for g in groupings.values():
        if g["name"].startswith("Dominio: "):
            for r in m.out[g["id"]]:
                if r["type"] == "AggregationRelationship" and r["target"] in m.el:
                    domain_by_name.setdefault(m.el[r["target"]]["name"], g["name"][len("Dominio: "):])
    md_agg_ctx: dict[str, str] = {}
    if docs_dir:
        for t in mdtables.tables(mdtables.read(docs_dir / "Fase05" / "01_mapa_de_contextos.md")):
            if t and t[0][0] == "Contexto" and "Agregados que contiene" in t[0]:
                col = t[0].index("Agregados que contiene")
                for row in t[1:]:
                    for name in [x.strip() for x in row[col].split(",")]:
                        md_agg_ctx[name] = row[0]

    aggs: dict[str, dict] = {}
    for d in m.of_type("DataObject"):
        ag = d["props"].get("Agregado")
        if not ag:
            continue
        a = aggs.setdefault(ag, {"name": ag, "context": None, "root": None, "entities": [], "value_objects": [],
                                 "structure": [], "commands": [], "events": []})
        role = d["props"].get("Rol", "")
        item = {"id": d["id"], "name": d["name"], "doc": d["doc"]}
        if role == "Raíz":
            a["root"] = item
            a["context"] = domain_by_name.get(ag) or domain_by_name.get(d["name"]) or md_agg_ctx.get(ag)
        elif role == "Entidad":
            a["entities"].append(item)
        elif role == "VO":
            a["value_objects"].append(item)
    for a in aggs.values():
        ids = {x["id"] for x in ([a["root"]] if a["root"] else []) + a["entities"] + a["value_objects"]}
        for pid in ids:
            for c in m.targets(pid, "CompositionRelationship"):
                if c["id"] in ids:
                    a["structure"].append({"parent": m.el[pid]["name"], "child": c["name"]})

    # ---- comandos y eventos ----
    events: dict[str, dict] = {}
    for e in m.of_type("ApplicationEvent"):
        events[e["id"]] = {"id": e["id"], "name": e["name"], "aggregate": e["props"].get("Agregado"),
                           "emitted_by": [], "triggers": [], "kind": "domain"}
    commands: dict[str, dict] = {}
    for p in m.of_type("ApplicationProcess"):
        ag = p["props"].get("Agregado")
        if not ag:
            continue
        roles = sorted({r["name"] for r in m.sources(p["id"], "AssociationRelationship") if r["type"] == "BusinessRole"} |
                       {r["name"] for r in m.targets(p["id"], "AssociationRelationship") if r["type"] == "BusinessRole"})
        emits = [events[t["id"]] for t in m.targets(p["id"], "TriggeringRelationship") if t["id"] in events]
        for ev in emits:
            ev["emitted_by"].append(p["name"])
        commands[p["id"]] = {"id": p["id"], "name": p["name"], "aggregate": ag, "roles": roles,
                             "emits": [x["name"] for x in emits], "doc": p["doc"]}
        if ag in aggs:
            aggs[ag]["commands"].append(p["name"])
    for ev in events.values():
        if ev["aggregate"] in aggs:
            aggs[ev["aggregate"]]["events"].append(ev["name"])

    ctx_of_agg = {n: a["context"] for n, a in aggs.items()}

    # ---- políticas: evento -> comando (dentro y entre contextos) ----
    policies, ext_events = [], {}
    for r in m.rels:
        if r["type"] != "TriggeringRelationship":
            continue
        s, t = m.el.get(r["source"]), m.el.get(r["target"])
        if not s or not t or t["id"] not in commands:
            continue
        if s["id"] in events:
            ev = events[s["id"]]
            policies.append({"event": ev["name"], "event_context": ctx_of_agg.get(ev["aggregate"]),
                             "command": t["name"], "command_context": ctx_of_agg.get(commands[t["id"]]["aggregate"]),
                             "external": False})
            ev["triggers"].append(t["name"])
        elif s["type"] == "BusinessEvent":
            ext_events[s["id"]] = s["name"]
            policies.append({"event": s["name"], "event_context": None, "command": t["name"],
                             "command_context": ctx_of_agg.get(commands[t["id"]]["aggregate"]), "external": True})

    # ---- contexto: agregados, servicios, interfaces ----
    for a in aggs.values():
        if a["context"] in contexts:
            contexts[a["context"]]["aggregates"].append(a["name"])
    for s in m.of_type("ApplicationService"):
        mt = re.search(r"contexto «([^»]+)»", s["doc"])
        if mt and mt.group(1) in contexts:
            contexts[mt.group(1)]["services"].append(s["name"])
    for i in m.of_type("ApplicationInterface"):
        mt = re.search(r"contexto «([^»]+)»", i["doc"])
        if mt and mt.group(1) in contexts:
            contexts[mt.group(1)]["interfaces"].append(i["name"])

    # ---- eventos publicados/consumidos (por políticas entre contextos) ----
    for p in policies:
        ec, cc = p["event_context"], p["command_context"]
        if ec and cc and ec != cc:
            if p["event"] not in contexts[ec]["published_events"]:
                contexts[ec]["published_events"].append(p["event"])
            if p["event"] not in contexts[cc]["consumed_events"]:
                contexts[cc]["consumed_events"].append(p["event"])
        elif p["external"] and cc:
            if p["event"] not in contexts[cc]["consumed_events"]:
                contexts[cc]["consumed_events"].append(p["event"])

    # ---- relaciones entre contextos (tabla de la Fase 5) ----
    relations = []
    if docs_dir:
        md = mdtables.read(docs_dir / "Fase05" / "01_mapa_de_contextos.md")
        for t in mdtables.tables(md):
            if t and "Contexto A (upstream)" in t[0][0]:
                for row in t[1:]:
                    if len(row) >= 7:
                        relations.append({
                            "upstream": row[0], "downstream": row[1], "pattern": row[3], "mechanism": row[5],
                            "events": re.findall(r"«([^»]+)»", row[5]), "sync": row[6],
                        })
    for rel in relations:
        up, down = rel["upstream"], rel["downstream"]
        for ev in rel["events"]:
            if up in contexts and ev not in contexts[up]["published_events"]:
                contexts[up]["published_events"].append(ev)
            if down in contexts and ev not in contexts[down]["consumed_events"]:
                contexts[down]["consumed_events"].append(ev)

    # ---- lenguaje ubicuo, roles y contratos ----
    ubiquitous = [{"term": b["name"], "context": b["props"].get("Contexto", ""), "definition": b["doc"],
                   "example": b["props"].get("Ejemplo", ""), "avoid": b["props"].get("No usar", "")}
                  for b in m.of_type("BusinessObject") if b["props"].get("Contexto")]
    roles = [{"id": r["id"], "name": r["name"], "doc": r["doc"]} for r in m.of_type("BusinessRole")]
    contracts = _contracts(m, docs_dir, list(contexts))

    ir = {
        "model": {"file": m.path.name, "sha": m.sha()},
        "contexts": list(contexts.values()),
        "aggregates": list(aggs.values()),
        "commands": list(commands.values()),
        "events": [{k: v for k, v in e.items()} for e in events.values()],
        "external_events": sorted(set(ext_events.values())),
        "policies": policies,
        "context_relations": relations,
        "roles": roles,
        "contracts": contracts,
        "ubiquitous_language": ubiquitous,
    }
    return ir


# Servicios N3 (subdominio) -> contexto. Los N4 heredan por composición; los N2 (plataforma) cruzan contextos.
N3_TO_CONTEXT = {
    "Registro de operación de flota": "Operación y Horas",
    "Gestión de flota y componentes": "Flota y Componentes",
    "Gestión del plan de mantenimiento": "Plan de Mantenimiento",
    "Gestión de órdenes de trabajo": "Intervenciones",
    "Gestión de repuestos del taller": "Repuestos del Taller",
    "Gestión de indicadores de mantenimiento": "Indicadores",
    "Verificación de habilitación de técnicos": "Habilitación de Personal",
}


def _service_context(m: Model, bs: dict) -> str | None:
    seen, cur = set(), [bs]
    while cur:
        x = cur.pop()
        if x["id"] in seen:
            continue
        seen.add(x["id"])
        if x["name"] in N3_TO_CONTEXT:
            return N3_TO_CONTEXT[x["name"]]
        cur += m.sources(x["id"], "CompositionRelationship")
    return None


def _contracts(m: Model, docs_dir: Path | None, context_names: list[str]) -> list[dict]:
    """Contratos de servicio (Fase 2) enriquecidos con la tabla Markdown (errores, pre/post, RNF)."""
    md_sections: dict[str, dict] = {}
    if docs_dir:
        text = mdtables.read(docs_dir / "Fase02" / "04_contratos_servicios.md")
        for title, body in mdtables.sections(text, 3).items():
            md_sections[re.sub(r"\s*\(N\d\)\s*$", "", title).strip()] = mdtables.key_value_table(body)
    out = []
    for c in m.of_type("Contract"):
        svc = c["props"].get("Servicio", "")
        bs = next((e for e in m.of_type("BusinessService") if e["name"] == svc), None)
        ctx = _service_context(m, bs) if bs else None
        kv = md_sections.get(svc, {})
        ops = re.search(r"Operaciones:\s*(.+)", c["doc"])
        ops_text = re.split(r"\.\s+(?:Entradas|Salidas|Errores|Pre|Post|Consumidores|Solo lectura)\b", ops.group(1))[0] if ops else ""
        out.append({
            "id": c["id"], "name": c["name"], "service": svc, "context": ctx, "level": c["props"].get("Nivel", ""),
            "version": c["props"].get("Versión", ""), "rnf": c["props"].get("RNF", ""),
            "operations": [o.strip(" .") for o in ops_text.split(";") if o.strip(" .")],
            "errors": [e.strip() for e in re.split(r"[;,]", kv.get("Errores y semántica", "")) if e.strip()],
            "preconditions": kv.get("Precondiciones / postcondiciones", ""),
            "consumers": kv.get("Consumidores", ""), "owner": kv.get("Dueño / responsable", ""),
            "inputs": kv.get("Entradas (objetos de negocio)", ""), "outputs": kv.get("Salidas", ""),
        })
    return out


# ---------------------------------------------------------------- validación
def validate_ir(ir: dict) -> tuple[list[str], list[str]]:
    """Devuelve (errores, avisos). Los errores detienen el pipeline."""
    errors, warns = [], []
    agg_names = {a["name"] for a in ir["aggregates"]}
    for a in ir["aggregates"]:
        if not a["root"]:
            errors.append(f"Agregado «{a['name']}» sin raíz (Rol=Raíz).")
        if not a["context"]:
            errors.append(f"Agregado «{a['name']}» sin contexto (no está en ningún «Dominio: …»).")
        if not a["commands"]:
            warns.append(f"Agregado «{a['name']}» sin comandos.")
    for c in ir["commands"]:
        if c["aggregate"] not in agg_names:
            errors.append(f"Comando «{c['name']}» apunta a un agregado inexistente: {c['aggregate']}.")
        if not c["emits"]:
            errors.append(f"Comando «{c['name']}» no emite ningún evento.")
    for e in ir["events"]:
        if not e["emitted_by"]:
            errors.append(f"Evento «{e['name']}» sin comando emisor.")
    ctx_names = {c["name"] for c in ir["contexts"]}
    for p in ir["policies"]:
        if p["command_context"] not in ctx_names:
            errors.append(f"Política «{p['event']} → {p['command']}» con contexto destino desconocido.")
    if not ir["policies"]:
        warns.append("El modelo no tiene políticas evento→comando.")
    return errors, warns


def pascal_name(text: str) -> str:
    return pascal(text)
