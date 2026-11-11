"""Información de un contexto del ArchiMate: qué contiene (agregados, comandos, reglas, eventos, dependencias). Solo hechos del modelo: el arquitecto decide con esta información delante."""
from __future__ import annotations

from .manifest import query_name



def facts(ir: dict, context: str) -> dict:
    ctx = next(c for c in ir["contexts"] if c["name"] == context)
    aggs = {a["name"]: a for a in ir["aggregates"]}
    own = [aggs[n] for n in ctx["aggregates"]]
    cmds = [c for c in ir["commands"] if aggs[c["aggregate"]]["context"] == context]
    contracts = [k for k in ir["contracts"] if k["context"] == context]
    per_agg = {a["name"]: sum(1 for c in cmds if c["aggregate"] == a["name"]) for a in own}
    rules = sorted({e for k in contracts for e in k["errors"]})
    queries = sorted({q for k in contracts for op in k["operations"] if (q := query_name(op))})
    sync_in = [r for r in ir["context_relations"] if r["downstream"] == context and (r["sync"].startswith("Síncrono") or r["mechanism"].startswith("API"))]
    rnf = " ".join(k.get("rnf", "") for k in contracts).lower()
    return {"context": context, "classification": ctx["classification"], "purpose": ctx["purpose"], "aggregates": [a["name"] for a in own],
            "commands": [c["name"] for c in cmds], "commands_per_aggregate": per_agg, "rules": rules, "queries": queries,
            "published": ctx["published_events"], "consumed": ctx["consumed_events"], "sync_in": sync_in,
            "personal_data": any(w in rnf for w in ("1581", "datos de personas", "datos personales"))}
