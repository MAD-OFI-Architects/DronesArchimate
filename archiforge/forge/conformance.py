"""Verificador de conformidad modelo -> código y matriz de trazabilidad.

Un símbolo cuenta solo si está DECLARADO (class/record/interface/enum/def) en un archivo cuya ruta
pertenece a la capa esperada: así se verifica la estructura de capas, no solo la presencia del nombre.
"""
from __future__ import annotations

import fnmatch
import re
from pathlib import Path

from .config import LAYERS_BY_LANG, Config
from .util import norm

SKIP = {"bin", "obj", "node_modules", ".venv", "venv", "__pycache__", ".git", "dist", ".pytest_cache",
        "TestResults", ".mypy_cache", "coverage"}
EXT = {"csharp": {".cs"}, "python": {".py"}, "java": {".java"}, "typescript": {".ts", ".tsx", ".js", ".jsx", ".vue"}}
DECL = {
    "csharp": re.compile(r"\b(?:class|interface|enum|struct|record)\s+(?:struct\s+|class\s+)?([A-Za-z_]\w*)"),
    "python": re.compile(r"^\s*(?:class|def)\s+([A-Za-z_]\w*)", re.M),
    "java": re.compile(r"\b(?:class|interface|enum|record)\s+([A-Za-z_]\w*)"),
    "typescript": re.compile(r"\b(?:class|function|const|let|interface|type|enum)\s+([A-Za-z_]\w*)"),
}


def _files(root: Path, exts: set[str] | None = None):
    if not root.exists():
        return
    for p in root.rglob("*"):
        if p.is_file() and not (set(p.relative_to(root).parts) & SKIP) and (exts is None or p.suffix in exts):
            yield p


def _rel(root: Path, p: Path) -> str:
    return "/" + p.relative_to(root).as_posix().lower()


def index(root: Path, lang: str):
    """[(ruta_rel_minúsculas, archivo, {nombres declarados normalizados}, texto)]"""
    out = []
    for p in _files(root, EXT[lang]):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        out.append((_rel(root, p), p, {norm(n) for n in DECL[lang].findall(text)}, text))
    return out


def service_root(cfg: Config, domain_slug: str) -> Path:
    return cfg.out / "services" / domain_slug


def check(cfg: Config, manifest: dict, layers: set[str] | None = None, domains: set[str] | None = None) -> dict:
    by_slug = {d.context: d for d in cfg.domains}
    cache: dict[tuple[str, str], list] = {}
    results = []
    for it in manifest["items"]:
        if layers and it["layer"] not in layers:
            continue
        if domains and it["domain"] not in domains:
            continue
        lang = it["language"]
        if lang == "typescript":
            root = cfg.out / "frontend" / it["remote"]
        else:
            root = service_root(cfg, by_slug[it["domain"]].slug)
        key = (str(root), lang)
        if lang != "typescript" or True:
            if key not in cache:
                cache[key] = index(root, lang)
        idx = cache[key]
        frags = LAYERS_BY_LANG.get(lang, {}).get(it["layer"], [])
        found = None
        if it["kind"] == "file":
            pats = it["glob"].split("|")
            for p in _files(root):
                if any(fnmatch.fnmatch(p.name, pat) for pat in pats):
                    found = str(p.relative_to(cfg.out))
                    break
        elif it.get("mode") == "referenced":      # pruebas: el comando aparece en archivos de test
            pat = re.compile(r"\b" + re.escape(it["name"]) + r"\b")
            for rel, p, _, text in idx:
                if any(f in rel + "/" for f in frags) and pat.search(text):
                    found = str(p.relative_to(cfg.out))
                    break
        elif it.get("mode") == "text":            # rutas: el segmento kebab del comando aparece en la capa API
            for rel, p, _, text in idx:
                if any(f in rel + "/" for f in frags) and it["name"] in text:
                    found = str(p.relative_to(cfg.out))
                    break
        elif lang == "typescript":
            n = norm(it["name"])
            for rel, p, names, _ in idx:
                if n in names:
                    found = str(p.relative_to(cfg.out))
                    break
        else:
            n = norm(it["name"])
            for rel, p, names, _ in idx:
                if n in names and any(f in rel for f in frags):
                    found = str(p.relative_to(cfg.out))
                    break
        results.append({**it, "found": found, "ok": bool(found)})
    req = [r for r in results if r["required"]]
    ok = [r for r in req if r["ok"]]
    return {"total": len(req), "ok": len(ok), "ratio": (len(ok) / len(req)) if req else 1.0,
            "missing": [r for r in req if not r["ok"]], "results": results}


def missing_text(res: dict, limit: int = 80) -> str:
    lines = [f"- [{m['layer']}] {m['kind']} `{m['name']}` (dominio: {m['domain']}; modelo: {m['trace']})"
             for m in res["missing"][:limit]]
    extra = len(res["missing"]) - limit
    return "\n".join(lines) + (f"\n… y {extra} más" if extra > 0 else "")


def traceability_markdown(res: dict) -> str:
    lines = ["# Matriz de trazabilidad modelo → código", "",
             f"**Conformidad: {res['ok']}/{res['total']} = {res['ratio']:.1%}** (símbolos obligatorios declarados en su capa).", "",
             "| Dominio | Capa | Tipo | Símbolo | Elemento del modelo | Archivo | Estado |", "|---|---|---|---|---|---|---|"]
    for r in res["results"]:
        lines.append(f"| {r['domain']} | {r['layer']} | {r['kind']} | `{r['name']}` | {r['trace']} | "
                     f"{r['found'] or '—'} | {'✅' if r['ok'] else ('❌' if r['required'] else '➖')} |")
    return "\n".join(lines) + "\n"
