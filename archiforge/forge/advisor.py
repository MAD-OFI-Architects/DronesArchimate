"""Asesor: lee el ArchiMate (IR) y RECOMIENDA patrones con su razón. Nunca decide: la decisión es del arquitecto.

Las señales son heurísticas simples sobre el modelo; cada recomendación dice qué señal la causa para que se pueda discutir.
Regla de diseño contra la sobreingeniería: sin señal, el patrón se marca «no necesario».
"""
from __future__ import annotations

from .manifest import query_name

R, O, N = "recomendado", "opcional", "no necesario"


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


def advise(ir: dict, context: str, catalog: dict) -> list[dict]:
    f = facts(ir, context)
    big = max(f["commands_per_aggregate"].values() or [0])
    rec: dict[str, tuple[str, str]] = {}
    nq, nr, ncmd = len(f["queries"]), len(f["rules"]), len(f["commands"])
    rec["cqrs"] = ((R, f"{nq} operaciones de lectura en los contratos y {ncmd} comandos: lectura y escritura tienen formas distintas.") if nq >= 4
                   else (O, f"solo {nq} operaciones de lectura: casos de uso simples pueden bastar.") if nq >= 1
                   else (N, "el contrato no declara consultas propias."))
    rec["pipeline"] = ((R, f"{ncmd} comandos que comparten validación y transacción.") if ncmd >= 6
                       else (O, f"{ncmd} comandos: un decorador o validación directa también sirve.") if ncmd >= 3
                       else (N, "muy pocos comandos para justificar una cadena."))
    rec["memento"] = (R, "el agregado se persiste como snapshot y debe reconstruirse validando; además lo pide la evaluación.")
    rec["state"] = ((R, f"un agregado tiene {big} comandos: ciclo de vida con transiciones.") if big >= 5
                    else (O, f"el agregado más activo tiene {big} comandos: un enum con validación puede alcanzar.") if big >= 3
                    else (N, "ciclo de vida corto: un enum alcanza."))
    rec["specification"] = ((R, f"{nr} reglas de negocio en los contratos: conviene componerlas.") if nr >= 8
                            else (O, f"{nr} reglas de negocio: úsalo si se reutilizan o combinan.") if nr >= 4
                            else (N, f"solo {nr} reglas de negocio."))
    pub, cons = f["published"], f["consumed"]
    rec["eventos"] = ((R, f"publica {len(pub)} y consume {len(cons)} eventos según el modelo.") if pub or cons
                      else (N, "el contexto no publica ni consume eventos."))
    rec["outbox"] = ((R, f"publica {len(pub)} evento(s): guardar y publicar debe ser atómico.") if pub
                     else (N, "no publica eventos."))
    up = sorted({r["upstream"] for r in f["sync_in"]})
    rec["acl"] = ((R, f"llama por API síncrona a {', '.join(up)}: protege tu dominio de su modelo.") if up
                  else (N, "no hay llamadas síncronas a otros contextos."))
    rec["cache"] = ((R, "hay lecturas frecuentes y/o llamadas a datos de referencia; además lo pide la evaluación.") if (nq >= 3 or up)
                    else (O, "pocas lecturas, pero la evaluación pide demostrar una caché.") )
    rec["cifrado"] = ((R, "los contratos exigen proteger datos personales (Ley 1581/2012); lo pide la evaluación.") if f["personal_data"]
                      else (O, "el modelo no declara datos personales en este contexto, pero la evaluación pide cifrado simple."))
    out = []
    for pid, spec in catalog.items():
        level, why = rec.get(pid, (N, "sin señal en el modelo."))
        out.append({"id": pid, "nombre": spec["nombre"], "recomendacion": level, "razon": why, "cuando_no": spec["cuando_no"],
                    "costo": spec["costo"], "evaluacion": bool(spec.get("evaluacion")), "requiere": spec.get("requiere", [])})
    return out


def render(ir: dict, context: str, catalog: dict) -> str:
    f = facts(ir, context)
    L = [f"# Contexto «{context}» ({f['classification']})", f"{f['purpose']}", "",
         f"- Agregados: {', '.join(f['aggregates'])} · Comandos: {len(f['commands'])} · Reglas de negocio (contratos): {len(f['rules'])} · Consultas: {len(f['queries'])}",
         f"- Publica: {', '.join(f['published']) or '—'} · Consume: {', '.join(f['consumed']) or '—'}",
         f"- APIs síncronas hacia otros contextos: {', '.join(sorted({r['upstream'] for r in f['sync_in']})) or '—'}", "",
         "## Patrones: recomendación (la decisión es tuya)", "",
         "| Patrón | Recomendación | Por qué | Cuándo NO | Costo | Eval. |", "|---|---|---|---|---|---|"]
    for a in advise(ir, context, catalog):
        L.append(f"| `{a['id']}` {a['nombre']} | **{a['recomendacion']}** | {a['razon']} | {a['cuando_no']} | {a['costo']} | {'sí' if a['evaluacion'] else ''} |")
    return "\n".join(L) + "\n"
