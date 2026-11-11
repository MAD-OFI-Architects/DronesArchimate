"""Manifiesto: lo que el MODELO exige que exista en el código (símbolos esperados, por capa).

Es determinista: el mismo IR produce el mismo manifiesto. El agente implementa; el verificador
(`conformance.py`) comprueba que cada símbolo esté DECLARADO en la capa correcta. De ahí sale
la matriz de trazabilidad modelo -> código y el porcentaje de conformidad (meta del curso: >= 90 %).
"""
from __future__ import annotations

import re

from . import interconexion
from .config import Domain
from .util import kebab, pascal

VERB_QUERY = {"consultar": "Obtener", "obtener": "Obtener", "listar": "Listar"}


def _item(domain: Domain, kind: str, layer: str, name: str, trace: str = "", required: bool = True, **extra) -> dict:
    return {"id": f"{domain.slug}:{layer}:{kind}:{name}", "domain": domain.context, "language": domain.language,
            "kind": kind, "layer": layer, "name": name, "trace": trace, "required": required, **extra}


def service_env(d: Domain, bus: int = 5100, sim: int = 5110, api_urls: dict[str, str] | None = None) -> dict:
    """Contrato de variables de entorno de un servicio (lo fija el orquestador; el servicio las LEE, no las inventa)."""
    db = d.slug.replace("-", "_")
    env = {"PORT": str(d.port), "BUS_URL": f"http://event-bus:{bus}", "SIMULATORS_URL": f"http://simulators:{sim}",
           "CIFRADO_CLAVE": "ZGV2LWtleS0zMi1ieXRlcy1sb25nLWZvci1hZXMtMjU2ISE="}   # clave de desarrollo en base64 (32 bytes)
    env.update(api_urls or {})        # <PROVEEDOR>_API_URL: real o simulado según el ensamblado (SIMULATORS_URL se conserva por compatibilidad)
    if d.database == "mongodb":
        env["MONGO_URL"] = f"mongodb://mongo:27017/{d.slug}?replicaSet=rs0"
        if d.language == "java":
            env["SPRING_DATA_MONGODB_URI"] = env["MONGO_URL"]
    else:
        if d.language == "python":
            env["DATABASE_URL"] = f"postgresql://forge:forge@postgres:5432/{db}"
        elif d.language == "csharp":
            env["DATABASE_URL"] = f"Host=postgres;Port=5432;Database={db};Username=forge;Password=forge"
        else:
            env.update(SPRING_DATASOURCE_URL=f"jdbc:postgresql://postgres:5432/{db}", SPRING_DATASOURCE_USERNAME="forge",
                       SPRING_DATASOURCE_PASSWORD="forge")
    return env


def error_to_rule(code: str) -> str:
    return pascal(code.replace("_", " ").lower())


def query_name(op: str) -> str | None:
    first, _, rest = op.strip().partition(" ")
    verb = VERB_QUERY.get(first.lower())
    return f"{verb}{pascal(rest)}" if verb and rest else None


def acl_text(mechanism: str) -> str:
    m = re.search(r"«([^»]+)»", mechanism)
    return m.group(1) if m else re.sub(r"^API\s+(de\s+)?", "", mechanism, flags=re.I)


def acl_name(mechanism: str) -> str:
    return pascal(acl_text(mechanism))


def build_manifest(ir: dict, domains: list[Domain]) -> dict:
    real = {d.context for d in domains}
    ctx = {c["name"]: c for c in ir["contexts"]}
    aggs = {a["name"]: a for a in ir["aggregates"]}
    items: list[dict] = []
    domain_info: dict[str, dict] = {}

    for d in domains:
        c = ctx[d.context]
        own_aggs = [aggs[n] for n in c["aggregates"]]
        cmds = [x for x in ir["commands"] if aggs[x["aggregate"]]["context"] == d.context]
        evs = [e for e in ir["events"] if e["aggregate"] in c["aggregates"]]
        P = pascal(d.context)

        # ---------------- dominio ----------------
        for a in own_aggs:
            root = pascal(a["root"]["name"])
            items.append(_item(d, "aggregate_root", "domain", root, a["root"]["id"]))
            if d.uses("memento"):
                items.append(_item(d, "memento", "domain", f"{root}Memento", a["root"]["id"]))
            items.append(_item(d, "repository_port", "domain", f"I{root}Repository", a["root"]["id"]))
            for e in a["entities"]:
                items.append(_item(d, "entity", "domain", pascal(e["name"]), e["id"]))
            for v in a["value_objects"]:
                items.append(_item(d, "value_object", "domain", pascal(v["name"]), v["id"]))
            # ---------------- infraestructura por agregado (caché + repositorio) ----------------
            items.append(_item(d, "repository", "infrastructure", f"Repositorio{root}", a["root"]["id"]))
            if d.uses("cache"):
                items.append(_item(d, "cache_decorator", "infrastructure", f"RepositorioCacheado{root}", a["root"]["id"]))
            # ---------------- aplicación por agregado (lado de lectura: solo con CQRS) ----------------
            if d.uses("cqrs"):
                items.append(_item(d, "dto", "application", f"{root}Dto", a["root"]["id"]))
                items.append(_item(d, "mapper", "application", f"{root}Mapeador", a["root"]["id"]))
                items.append(_item(d, "query", "application", f"Obtener{root}Consulta", a["root"]["id"]))
                items.append(_item(d, "query_handler", "application", f"Obtener{root}Manejador", a["root"]["id"]))
            if d.style == "monolito-modular":      # cada agregado es un módulo con fachada pública (única puerta de entrada)
                items.append(_item(d, "module_facade", "contracts", f"I{root}Modulo", a["root"]["id"]))
        for e in evs:
            items.append(_item(d, "domain_event", "domain", pascal(e["name"]), e["id"]))

        rules = []
        for k in ir["contracts"]:
            if k["context"] == d.context:
                for code in k["errors"]:
                    if code not in rules:
                        rules.append(code)
        for code in rules:
            items.append(_item(d, "business_rule", "domain", error_to_rule(code), code))

        # ---------------- aplicación: comandos ----------------
        for x in cmds:
            n = pascal(x["name"])
            items.append(_item(d, "command", "application", f"{n}Comando", x["id"]))
            items.append(_item(d, "command_handler", "application", f"{n}Manejador", x["id"]))
            items.append(_item(d, "validator", "application", f"{n}Validador", x["id"]))
            items.append(_item(d, "request_model", "api", f"{n}Solicitud", x["id"]))
            items.append(_item(d, "test", "tests", f"{n}Comando", x["id"], mode="referenced"))
        seen_q = {f"Obtener{pascal(aggs[n]['root']['name'])}" for n in c["aggregates"]}
        for k in (ir["contracts"] if d.uses("cqrs") else []):
            if k["context"] == d.context:
                for op in k["operations"]:
                    q = query_name(op)
                    if q and q not in seen_q:
                        seen_q.add(q)
                        items.append(_item(d, "query", "application", f"{q}Consulta", k["id"]))
                        items.append(_item(d, "query_handler", "application", f"{q}Manejador", k["id"]))

        # ---------------- integración: publicados / consumidos (solo con el patrón «eventos») ----------------
        consumed_map = {}
        if d.uses("eventos"):
            for ev in c["published_events"]:
                n = pascal(ev)
                items.append(_item(d, "published_contract", "contracts", f"{n}V1", ev))
                items.append(_item(d, "event_translator", "application", f"{n}Traductor", ev))
            items.append(_item(d, "topics", "contracts", f"{P}Topicos", d.context))
            for ev in c["consumed_events"]:
                targets = [p["command"] for p in ir["policies"] if p["event"] == ev and p["command_context"] == d.context]
                if targets:
                    consumed_map[ev] = targets
                    items.append(_item(d, "event_consumer", "application", f"{pascal(ev)}Consumidor", ev, triggers=targets))
            for p in ir["policies"]:
                if p["event_context"] == d.context and p["command_context"] == d.context:
                    items.append(_item(d, "policy_observer", "application", f"{pascal(p['event'])}Observador", p["event"],
                                       triggers=[p["command"]]))

        # ---------------- ACL hacia contextos simulados (síncronos / API) ----------------
        acl = []
        for r in ir["context_relations"]:
            # El ACL se genera para TODO proveedor síncrono: si ya es real, la URL cambia (compose), el adaptador no.
            if d.uses("acl") and r["downstream"] == d.context and r["upstream"] in ctx \
                    and (r["sync"].startswith("Síncrono") or r["mechanism"].startswith("API")):
                nm = acl_name(r["mechanism"])
                acl.append({"name": nm, "slug": kebab(acl_text(r["mechanism"])), "upstream": r["upstream"], "mechanism": r["mechanism"],
                            "sync": r["sync"], "env": interconexion.env_var(r["upstream"]), "upstream_real": r["upstream"] in real})
                items.append(_item(d, "acl_port", "application", f"I{nm}", r["upstream"]))
                items.append(_item(d, "acl_adapter", "infrastructure", f"{nm}Adapter", r["upstream"]))

        # ---------------- transversales (cada uno solo si el arquitecto lo eligió) ----------------
        if d.uses("cifrado"):
            items.append(_item(d, "crypto_port", "application", "Cifrador"))
            items.append(_item(d, "crypto_impl", "infrastructure", "CifradorAes"))
        if d.uses("eventos"):
            items.append(_item(d, "event_publisher", "infrastructure", "PublicadorDeEventosHttp"))
        items.append(_item(d, "endpoints", "api", f"{P}Endpoints", d.context))
        items.append(_item(d, "composition_root", "api", f"{P}Composicion", d.context))
        if d.uses("outbox"):
            for n in ("BandejaDeSalida", "ProcesadorDeMensajeEntrante"):
                items.append(_item(d, "infra_pattern", "infrastructure", n))
        if d.style == "soa":      # SOA: servicio de grano grueso con contrato explícito y orquestación
            items.append(_item(d, "soa_orchestrator", "application", f"Orquestador{P}", d.context))
            items.append(_item(d, "file", "ops", "contrato-servicio", glob="openapi.yaml|openapi.yml|openapi.json"))
            items.append(_item(d, "file", "ops", "catalogo-de-servicios", glob="catalogo-de-servicios.md"))
        if d.style == "monolito-modular":
            items.append(_item(d, "module_registry", "api", f"{P}Modulos", d.context))
        items.append(_item(d, "file", "ops", "Dockerfile", glob="Dockerfile"))
        items.append(_item(d, "file", "ops", "README.md", glob="README.md"))
        items.append(_item(d, "file", "ops", "proyecto", glob={"csharp": "*.sln|*.slnx", "python": "pyproject.toml|requirements.txt",
                                                                "java": "pom.xml"}[d.language]))

        # rutas HTTP (comprobadas como texto en la capa API)
        routes = []
        for a in own_aggs:
            seg = kebab(a["name"])
            first = True
            for cname in a["commands"]:
                cm = next(x for x in cmds if x["name"] == cname)
                path = f"/api/{seg}" if first else f"/api/{seg}/{{id}}/{kebab(cname)}"
                routes.append({"method": "POST", "path": path, "command": cname, "roles": cm["roles"]})
                # la ruta de creación (POST /api/<agregado>) no lleva el nombre del comando en el path
                items.append(_item(d, "route", "api", f"/api/{seg}" if first else kebab(cname), cm["id"], mode="text"))
                first = False
            routes.append({"method": "GET", "path": f"/api/{seg}/{{id}}", "command": None, "roles": []})
        # contrato síncrono: lo que OTROS contextos (reales o simulados) le piden a este servicio por API
        provided = [l for l in interconexion.sync_links(ir) if l["upstream"] == d.context and l["explicit"]]
        for slug_ in dict.fromkeys(l["slug"] for l in provided):
            items.append(_item(d, "route", "api", f"/api/{slug_}", mode="text"))
        domain_info[d.context] = {
            "slug": d.slug, "language": d.language, "architecture": d.architecture, "style": d.style, "database": d.database,
            "port": d.port, "patterns": sorted(p for p in d.patterns if d.uses(p)),
            "env": service_env(d, api_urls=interconexion.api_urls(ir, d, domains)), "provides": [{"slug": sl, "consumers": sorted({x["downstream"] for x in provided if x["slug"] == sl})} for sl in dict.fromkeys(l["slug"] for l in provided)],
            "aggregates": c["aggregates"], "commands": [x["name"] for x in cmds],
            "published_events": c["published_events"], "consumed": consumed_map, "acl": acl, "routes": routes,
            "business_rules": rules,
        }

    # ---------------- microfrontends: UN remote por dominio (cada equipo es dueño del suyo); los roles se filtran dentro ----------------
    frontend = {"shell": "mfe-shell", "remotes": []}
    for d in domains:
        slug = f"mfe-{d.slug}"
        cmds_, roles = [], {}
        for x in ir["commands"]:
            if aggs[x["aggregate"]]["context"] == d.context and x["roles"]:
                cm = {"command": x["name"], "context": d.context, "aggregate": x["aggregate"], "roles": x["roles"]}
                cmds_.append(cm)
                for r in x["roles"]:
                    roles.setdefault(r, []).append(x["name"])
                items.append({"id": f"frontend:{d.slug}:form:{pascal(x['name'])}", "domain": d.context, "language": "typescript",
                              "kind": "form", "layer": "frontend", "name": f"{pascal(x['name'])}Form", "trace": x["name"],
                              "required": True, "remote": slug})
        if cmds_:
            frontend["remotes"].append({"slug": slug, "context": d.context, "domain_slug": d.slug, "roles": roles, "commands": cmds_})

    # ---------------- simulación de los demás contextos ----------------
    simulated = []
    real_published = {e for n_ in real for e in ctx[n_]["published_events"]}
    for c in ir["contexts"]:
        if c["name"] in real:
            continue
        emits = [e for e in c["published_events"] if any(
            p["event"] == e and p["command_context"] in real for p in ir["policies"])]
        subs = [e for e in c["consumed_events"] if e in real_published]
        simulated.append({"context": c["name"], "emits": emits, "subscribes": subs,
                          "sync_apis": [r["mechanism"] for r in ir["context_relations"]
                                        if r["upstream"] == c["name"] and r["downstream"] in real and r["sync"].startswith("Síncrono")]})
    return {"items": items, "domains": domain_info, "frontend": frontend,
            "simulated": [s for s in simulated if s["emits"] or s["subscribes"] or s["sync_apis"]]}


def summary(m: dict) -> dict:
    by = {}
    for it in m["items"]:
        by[(it["domain"], it["layer"])] = by.get((it["domain"], it["layer"]), 0) + 1
    return {f"{d} / {l}": n for (d, l), n in sorted(by.items())}
