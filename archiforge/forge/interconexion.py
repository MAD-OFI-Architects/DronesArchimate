"""Interconexión síncrona entre contextos (APIs): quién llama a quién y a qué URL.

Los eventos ya se resuelven en el bus (`scaffold.bus_topics`). Las llamadas síncronas (relaciones «Síncrono»/«API …» del ArchiMate)
se resuelven aquí con UNA regla, válida para cualquier par de contextos:

    proveedor REAL      -> http://<slug>:<puerto>/api            (el servicio que construyó otro equipo)
    proveedor SIMULADO  -> http://simulators:<puerto>/api/<contexto>

El consumidor lee SIEMPRE la variable `<CONTEXTO>_API_URL` y llama a `<URL>/<operación>`: no sabe (ni debe saber) si al otro lado hay un
servicio real o un simulador. Cuando alguien construye el proveedor y se vuelve a ensamblar, el compose cambia la URL y listo.
"""
from __future__ import annotations

from .config import Domain
from .util import kebab

SIM_PORT = 5110


def env_var(upstream: str) -> str:
    """`Habilitación de Personal` -> `HABILITACION_DE_PERSONAL_API_URL`."""
    return kebab(upstream).replace("-", "_").upper() + "_API_URL"


def sync_links(ir: dict) -> list[dict]:
    """Relaciones síncronas del modelo: {downstream (consumidor), upstream (proveedor), name, slug (operación), env, explicit}."""
    from .manifest import acl_name, acl_text          # import local: manifest también usa este módulo
    out, seen = [], set()
    for r in ir["context_relations"]:
        if r["sync"].startswith("Síncrono") or r["mechanism"].startswith("API"):
            link = {"downstream": r["downstream"], "upstream": r["upstream"], "name": acl_name(r["mechanism"]),
                    "slug": kebab(acl_text(r["mechanism"])), "mechanism": r["mechanism"], "env": env_var(r["upstream"]),
                    # «API …» nombra una operación concreta (el proveedor debe exponer /api/<operación>); una «Consulta de solo lectura»
                    # es genérica: el consumidor usa los GET que el proveedor ya publica en su manifiesto.
                    "explicit": r["mechanism"].startswith("API")}
            key = (link["downstream"], link["upstream"], link["slug"])
            if key not in seen:
                seen.add(key)
                out.append(link)
    return out


def api_urls(ir: dict, d: Domain, real: list[Domain], sim: int = SIM_PORT, simulated: bool = True) -> dict[str, str]:
    """Variables `<PROVEEDOR>_API_URL` del servicio `d`, según quién es real en este ensamblado."""
    by_ctx = {x.context: x for x in real}
    urls: dict[str, str] = {}
    for l in sync_links(ir):
        if l["downstream"] != d.context:
            continue
        up = by_ctx.get(l["upstream"])
        if up:
            urls[l["env"]] = f"http://{up.slug}:{up.port}/api"
        elif simulated:
            urls[l["env"]] = f"http://simulators:{sim}/api/{kebab(l['upstream'])}"
        else:
            urls[l["env"]] = "${" + l["env"] + ":-}"        # sin simuladores: la URL del proveedor la pone el equipo
    return urls
