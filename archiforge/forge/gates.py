"""Puertas de calidad: cada etapa solo avanza si TODAS sus puertas pasan.

Cada puerta devuelve (ok, detalle). El detalle se realimenta al agente en el siguiente intento.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from . import conformance
from .config import Config
from .util import norm

TAIL = 6000


@dataclass
class Gate:
    ok: bool
    name: str
    detail: str = ""
    skipped: bool = False


def run_cmd(argv: list[str], cwd: Path, timeout: int = 900, env: dict | None = None) -> tuple[int, str]:
    exe = shutil.which(argv[0])
    if not exe:
        return 127, f"No se encontró '{argv[0]}' en el PATH."
    argv = [exe] + argv[1:]
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, **(env or {})}, errors="replace")
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out[-TAIL:]
    except subprocess.TimeoutExpired:
        return 124, f"Tiempo agotado ({timeout}s): {' '.join(argv[:3])}"


def _svc(cfg: Config, slug: str) -> Path:
    return cfg.out / "services" / slug


# ------------------------------------------------------------------ C#
def dotnet_build(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    if not root.exists():
        return Gate(False, "dotnet build", f"No existe {root}.")
    code, out = run_cmd(["dotnet", "build", "--nologo", "-v", "q"], root)
    return Gate(code == 0, "dotnet build", out)


def dotnet_test(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    code, out = run_cmd(["dotnet", "test", "--nologo", "-v", "q"], root, timeout=1500)
    return Gate(code == 0, "dotnet test", out)


# Grafo de referencias permitido entre proyectos de un microservicio (regla de dependencias; clean-ddd y hexagonal comparten la dirección)
ALLOWED_REFS = {
    "domain": {"domain"},                                   # + BuildingBlocks.Domain
    "contracts": set(),
    "application": {"domain", "contracts", "application"},
    "infrastructure": {"domain", "contracts", "application", "infrastructure"},
    "api": {"domain", "contracts", "application", "infrastructure", "api", "adapters.outbound", "adapters.inbound"},
    "adapters.outbound": {"domain", "contracts", "application", "adapters.outbound"},
    "adapters.inbound": {"domain", "contracts", "application", "adapters.outbound", "adapters.inbound"},
}


def arch_csproj(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    bad, seen = [], 0
    for proj in root.rglob("*.csproj"):
        if set(proj.parts) & conformance.SKIP:
            continue
        name = proj.stem.lower()
        layer = next((l for l in ALLOWED_REFS if name.endswith("." + l)), None)
        if not layer:
            continue
        seen += 1
        text = proj.read_text(encoding="utf-8", errors="ignore")
        for ref in re.findall(r'ProjectReference\s+Include="([^"]+)"', text):
            tgt = Path(ref.replace("\\", "/")).stem.lower()
            if tgt.startswith("buildingblocks."):
                bl = tgt.split(".", 1)[1]
                if layer == "domain" and bl != "domain":
                    bad.append(f"{proj.stem} (Domain) solo puede referenciar BuildingBlocks.Domain, referencia {tgt}.")
                continue
            tl = next((l for l in ALLOWED_REFS if tgt.endswith("." + l)), None)
            if tl and tl not in ALLOWED_REFS[layer]:
                bad.append(f"{proj.stem} ({layer}) no puede referenciar {tgt} ({tl}): rompe la regla de dependencias.")
    if not seen:
        return Gate(False, "arquitectura (.csproj)", f"No hay proyectos *.Domain/*.Application/… en {root}.")
    return Gate(not bad, "arquitectura (.csproj)", "\n".join(bad) or f"{seen} proyectos respetan la regla de dependencias.")


# ------------------------------------------------------------------ Python
def _venv_python(root: Path) -> Path:
    return root / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")


def py_setup(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    if not root.exists():
        return Gate(False, "python setup", f"No existe {root}.")
    py = _venv_python(root)
    if not py.exists():
        code, out = run_cmd([sys.executable, "-m", "venv", ".venv"], root)
        if code:
            return Gate(False, "python setup", out)
    reqs = []
    if (root / "requirements.txt").exists():
        reqs.append(["-r", "requirements.txt"])
    if (root / "pyproject.toml").exists():
        reqs.append(["-e", ".[dev]"])
    for req in reqs:
        code, out = run_cmd([str(py), "-m", "pip", "install", "-q", *req], root, timeout=900)
        if code and req[-1] == ".[dev]":      # el extra [dev] puede no existir
            code, out = run_cmd([str(py), "-m", "pip", "install", "-q", "-e", "."], root, timeout=900)
        if code:
            return Gate(False, "python setup", out)
    if not reqs:
        return Gate(False, "python setup", "Falta pyproject.toml o requirements.txt con las dependencias (incluye pytest).")
    return Gate(True, "python setup", "entorno listo")


def pytest_gate(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    setup = py_setup(cfg, slug)
    if not setup.ok:
        return setup
    code, out = run_cmd([str(_venv_python(root)), "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"], root, timeout=1200)
    return Gate(code == 0, "pytest", out)


PY_FORBIDDEN = {  # capa -> prefijos de módulo que NO puede importar (válido para clean-ddd y hexagonal)
    "domain": ("application", "adapters", "contracts", "infrastructure", "api"),
    "application": ("adapters", "infrastructure", "api"),
    "contracts": ("domain", "application", "adapters", "infrastructure", "api"),
}
DOMAIN_ALLOWED_3RD = {"typing", "dataclasses", "enum", "abc", "uuid", "datetime", "decimal", "re", "functools", "collections",
                      "__future__", "copy", "itertools", "math", "typing_extensions", "types", "contextlib", "operator"}


def arch_python(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    bad, seen = [], 0
    for f in conformance._files(root, {".py"}):
        rel = f.relative_to(root).as_posix().lower()
        layer = next((l for l in PY_FORBIDDEN if f"/{l}/" in "/" + rel), None)
        if not layer or "/tests/" in "/" + rel:
            continue
        seen += 1
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError as e:
            bad.append(f"{rel}: error de sintaxis {e}")
            continue
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [("." * node.level) + (node.module or "")]
            for mod in mods:
                parts = [p for p in mod.strip(".").split(".") if p]
                if any(p in PY_FORBIDDEN[layer] for p in parts):
                    bad.append(f"{rel}: la capa {layer} no puede importar «{mod}».")
                elif layer == "domain" and parts and not mod.startswith(".") and parts[0] not in DOMAIN_ALLOWED_3RD \
                        and parts[0] != Path(root).name.replace("-", "_") and not _is_local(root, parts[0]):
                    bad.append(f"{rel}: el dominio debe ser puro, importa la librería externa «{mod}».")
    if not seen:
        return Gate(False, "arquitectura (imports)", f"No hay código en domain/, application/ o contracts/ de {root}.")
    return Gate(not bad, "arquitectura (imports)", "\n".join(bad[:40]) or f"{seen} archivos respetan la hexagonal.")


DEFINICION_PY = re.compile(r"^class\s+([A-Za-z_]\w*)\s*(?:\(([^)]*)\))?", re.M)
DEFINICION_CS = re.compile(r"^\s*(?:public|internal)?\s*(?:sealed\s+|partial\s+|static\s+)*class\s+([A-Za-z_]\w*)\s*(?::([^\n{]*))?", re.M)
DEFINICION_JAVA = re.compile(r"^\s*(?:public\s+)?(?:final\s+|abstract\s+)*class\s+([A-Za-z_]\w*)\s*(?:extends\s+[\w.<>]+\s*)?(?:implements\s+([^\n{]*))?", re.M)
SALIDA_JAVA = re.compile(r"/(?:infrastructure|adapters/outbound)/")
SALIDA_PY = re.compile(r"/adapters/outbound/")
SALIDA_CS = re.compile(r"/(?:[^/]+\.)?Infrastructure/")


def wiring_gate(cfg: Config, d) -> Gate:
    """Un adaptador que nadie instancia es un patrón de adorno: existe para la diapositiva, no para el sistema.

    Revisa solo la capa de salida (adapters/outbound en Python, *.Infrastructure en C#), que es donde viven
    persistencia, cifrado, caché, bus y ACL. Los adaptadores de entrada quedan fuera a propósito: los invoca el
    framework HTTP, así que no se referencian desde otro archivo. Toda clase concreta de salida debe nombrarse
    desde un archivo de producción distinto al suyo; una clase que solo aparece en su propio archivo o en los
    tests es código muerto que finge cumplir un patrón.
    """
    root = _svc(cfg, d.slug)
    ext, patron, salida = {"python": (".py", DEFINICION_PY, SALIDA_PY), "csharp": (".cs", DEFINICION_CS, SALIDA_CS),
                           "java": (".java", DEFINICION_JAVA, SALIDA_JAVA)}[d.language]
    todos = list(conformance._files(root, {ext}))
    archivos = [f for f in todos if salida.search(f.as_posix())]
    if not archivos:
        return Gate(True, "cableado de adaptadores", f"{root} todavía no tiene adaptadores de salida.")
    textos = {f: f.read_text(encoding="utf-8", errors="ignore") for f in todos}
    muertos = []
    for f in archivos:
        for nombre, padres in patron.findall(textos[f]):
            if nombre.startswith("_") or "abstract" in padres or "ABC" in padres or "Protocol" in padres:
                continue
            if nombre.endswith(("Base", "Memento", "Exception")) or nombre.startswith(("RelojSimulado",)):
                continue
            # Dobles de prueba del esqueleto de mensajería durable (los usan las pruebas canónicas, no producción).
            if nombre.endswith("EnMemoria") and "ARCHIFORGE: mensajeria-durable" in textos[f]:
                continue
            usado = any(otro != f and "/tests/" not in otro.as_posix() and re.search(rf"\b{nombre}\b", texto)
                        for otro, texto in textos.items())
            if not usado:
                muertos.append(f"{f.relative_to(root).as_posix()}: «{nombre}» no se instancia ni se referencia fuera de su archivo.")
    detalle = "\n".join(sorted(muertos)[:20])
    return Gate(not muertos, "cableado de adaptadores",
                detalle or f"{len(archivos)} archivos de adaptadores de salida: todo lo definido se usa.")


def solid_gate(cfg: Config, d) -> Gate:
    """SOLID comprobado en el código real (SRP, OCP, LSP, ISP, DIP); ver forge/solid.py para las señales que se miden."""
    from . import solid
    root = _svc(cfg, d.slug)
    if not root.exists():
        return Gate(True, "SOLID", f"{root} todavía no existe.")
    found = solid.scan(root, d.language)
    return Gate(not found, "SOLID", "\n".join(str(f) for f in found[:30]) or "sin violaciones detectables de SRP, OCP, LSP, ISP ni DIP.")


def _is_local(root: Path, top: str) -> bool:
    return any((root / base / top).exists() or (root / base / f"{top}.py").exists() for base in ("", "src"))


# ------------------------------------------------------------------ Java
def maven_test(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    if not (root / "pom.xml").exists():
        return Gate(False, "mvn test", f"No existe pom.xml en {root}.")
    code, out = run_cmd(["mvn", "-q", "-B", "-ntp", "test"], root, timeout=1800)
    return Gate(code == 0, "mvn test", out)


JAVA_FORBIDDEN = {  # capa -> fragmentos de paquete que NO puede importar
    "domain": (".application.", ".infrastructure.", ".api.", ".adapters.", ".contracts.", "org.springframework", "jakarta.persistence",
               "com.mongodb", "org.springframework.data", "com.fasterxml", "javax.persistence"),
    "application": (".infrastructure.", ".api.", ".adapters.", "org.springframework.web", "jakarta.persistence", "com.mongodb"),
    "contracts": (".domain.", ".application.", ".infrastructure.", ".api.", ".adapters."),
}


def arch_java(cfg: Config, slug: str) -> Gate:
    root = _svc(cfg, slug)
    bad, seen = [], 0
    for f in conformance._files(root / "src" / "main", {".java"}) if (root / "src" / "main").exists() else []:
        rel = "/" + f.relative_to(root).as_posix().lower()
        layer = next((l for l in JAVA_FORBIDDEN if f"/{l}/" in rel), None)
        if not layer:
            continue
        seen += 1
        for imp in re.findall(r"^\s*import\s+(?:static\s+)?([\w.]+)", f.read_text(encoding="utf-8", errors="ignore"), re.M):
            if any(frag in "." + imp + "." or imp.startswith(frag) for frag in JAVA_FORBIDDEN[layer]):
                bad.append(f"{rel}: la capa {layer} no puede importar «{imp}».")
    if not seen:
        return Gate(False, "arquitectura (imports Java)", f"No hay código Java en domain/, application/ o contracts/ de {root}/src/main.")
    return Gate(not bad, "arquitectura (imports Java)", "\n".join(bad[:40]) or f"{seen} archivos respetan la regla de dependencias.")


def build_gates(cfg: Config, d, layers: set[str] | None, label: str) -> list[Gate]:
    """Puertas de una capa del dominio `d`: conformidad (si hay capas) + compilar/probar + regla de dependencias del lenguaje."""
    m = json.loads((cfg.root / cfg.state_dir / "manifest.json").read_text(encoding="utf-8"))
    g = [conformance_gate(cfg, m, layers, {d.context}, 1.0, label)] if layers else []
    if d.language == "csharp":
        g += [dotnet_build(cfg, d.slug), dotnet_test(cfg, d.slug), arch_csproj(cfg, d.slug)]
    elif d.language == "python":
        g += [pytest_gate(cfg, d.slug), arch_python(cfg, d.slug)]
    else:
        g += [maven_test(cfg, d.slug), arch_java(cfg, d.slug)]
    # El cableado se exige donde se ensamblan los adaptadores (etapa de adaptadores): antes, los esqueletos sembrados en S02
    # (p. ej. la mensajería durable) todavía no tienen composition root y no deben fallar las capas de dominio/aplicación.
    if layers is None or "infrastructure" in layers:
        g += [wiring_gate(cfg, d)]
    g += [solid_gate(cfg, d)]
    return g


# ------------------------------------------------------------------ Front
def npm_build(cfg: Config, rel: str) -> Gate:
    root = cfg.out / rel
    if not (root / "package.json").exists():
        return Gate(False, f"npm build {rel}", f"No existe package.json en {root}.")
    code, out = run_cmd(["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"], root, timeout=900)
    if code:
        return Gate(False, f"npm install {rel}", out)
    code, out = run_cmd(["npm", "run", "build"], root, timeout=900)
    return Gate(code == 0, f"npm build {rel}", out)


# ------------------------------------------------------------------ Conformidad y documentos
def conformance_gate(cfg: Config, manifest: dict, layers: set[str] | None, domains: set[str] | None,
                     threshold: float = 1.0, name: str = "conformidad con el modelo") -> Gate:
    res = conformance.check(cfg, manifest, layers, domains)
    ok = res["ratio"] >= threshold
    head = f"{res['ok']}/{res['total']} símbolos del modelo declarados ({res['ratio']:.1%}; exigido {threshold:.0%})."
    return Gate(ok, name, head + ("" if ok else "\nFaltan:\n" + conformance.missing_text(res)))


ADR_SECTIONS = ["arquitectura", "base de datos", "patrones", "estilo", "despliegue", "microfrontend"]


def adr_path(cfg: Config) -> Path:
    return cfg.out / "docs" / cfg.domains[0].slug / "decisiones-arquitectura.md"


def adr_gate(cfg: Config, manifest: dict, final: bool = True) -> Gate:
    """El ADR existe, trata las decisiones, cita clases REALES y cubre cada patrón que el arquitecto eligió."""
    doc = adr_path(cfg)
    if not doc.exists():
        return Gate(False, "ADR", f"Falta {doc.relative_to(cfg.root)}.")
    text = doc.read_text(encoding="utf-8")
    low = text.lower()
    miss = [s for s in ADR_SECTIONS if s not in low]
    problems = [f"El documento no trata: {', '.join(miss)}."] if miss else []
    if not final:
        return Gate(not problems, "ADR (estructura)", "\n".join(problems) or "ok")
    d = cfg.domains[0]
    cat = decisions_catalog(cfg)
    rows = [r for r in re.findall(r"^\|(.+)\|\s*$", text, re.M) if "---" not in r]
    pat_rows = [[c.strip() for c in r.split("|")] for r in rows if "patrón" not in r.lower() and "patron" not in r.lower()]
    for pid, p in d.patterns.items():
        if p.get("usar") and cat.get(pid) and not any(norm(cat[pid]["nombre"]) in norm(" ".join(r)) or pid in norm(r[0]) for r in pat_rows):
            problems.append(f"El patrón elegido «{cat[pid]['nombre']}» no aparece en la tabla de patrones del ADR.")
    checked = 0
    for cells in pat_rows:
        for cell in cells:
            for sym in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", cell):
                checked += 1
                if not any(sym in t for _, _, _, t in _all_code(cfg)):
                    problems.append(f"El patrón cita la clase `{sym}` pero no existe en el código.")
    if checked == 0:
        problems.append("La tabla de patrones no cita ninguna clase real entre comillas invertidas (`Clase`).")
    return Gate(not problems, "ADR (decisiones y patrones)", "\n".join(problems[:30]) or f"ADR completo; {checked} clases verificadas.")


def decisions_catalog(cfg: Config) -> dict:
    import tomllib
    return tomllib.loads((cfg.tool_root / "catalog" / "patrones.toml").read_text(encoding="utf-8"))


def _all_code(cfg: Config):
    out = []
    for d in cfg.domains:
        out += conformance.index(_svc(cfg, d.slug), d.language)
    return out


def files_gate(cfg: Config, paths: list[str], name: str = "archivos esperados") -> Gate:
    miss = [p for p in paths if not (cfg.out / p).exists()]
    return Gate(not miss, name, ("Faltan: " + ", ".join(miss)) if miss else "ok")


def report_gate(cfg: Config, rel: str, must_contain: list[str]) -> Gate:
    p = cfg.out / rel
    if not p.exists():
        return Gate(False, f"documento {rel}", "No existe.")
    t = p.read_text(encoding="utf-8", errors="ignore").lower()
    miss = [m for m in must_contain if m.lower() not in t]
    return Gate(not miss, f"documento {rel}", ("Le falta: " + ", ".join(miss)) if miss else "ok")


def _compose_up(plat: Path, project: str, port: int, name: str) -> tuple[bool, str, dict]:
    env = {"GATEWAY_PORT": str(port), "COMPOSE_PROJECT": project, "GATEWAY_URL": f"http://localhost:{port}"}
    code, out = run_cmd(["docker", "compose", "up", "-d", "--build", "--wait"], plat, timeout=2400, env=env)
    if code:
        _, logs = run_cmd(["docker", "compose", "logs", "--tail", "60"], plat, env=env)
        return False, f"docker compose up falló:\n{out}\n--- logs ---\n{logs}", env
    return True, "", env


def smoke_domain_gate(cfg: Config, d) -> Gate:
    """Humo AISLADO de un dominio: su servicio real + bus + simuladores de todo lo demás, con proyecto y puerto propios
    (así varios dominios, o varias personas, pueden correr su humo a la vez sin chocar)."""
    import zlib
    script = cfg.out / d.dir / "smoke" / "smoke.py"
    plat = cfg.out / ".platform" / d.slug
    if not script.exists():
        return Gate(False, "smoke del dominio", f"Falta {script.relative_to(cfg.out)}")
    if not (plat / "docker-compose.yml").exists():
        return Gate(False, "smoke del dominio", "No existe la plataforma de humo (la genera la etapa S02-scaffold).")
    port = 18000 + zlib.crc32(d.slug.encode()) % 2000
    ok, detail, env = _compose_up(plat, f"forge-{d.slug}", port, d.slug)
    try:
        if not ok:
            return Gate(False, "docker compose up (dominio)", detail)
        time.sleep(3)
        code, out = run_cmd([sys.executable, str(script)], cfg.out, timeout=900, env=env)
        return Gate(code == 0, "smoke del dominio", out)
    finally:
        run_cmd(["docker", "compose", "down", "-v"], plat, timeout=300, env=env)


def smoke_assembled_gate(cfg: Config, domains: list) -> Gate:
    """Humo del ENSAMBLADO: todos los dominios reales juntos; corre el smoke de cada uno contra el compose completo."""
    scripts = [(d, cfg.out / d.dir / "smoke" / "smoke.py") for d in domains]
    missing = [d.slug for d, sc in scripts if not sc.exists()]
    if missing:
        return Gate(False, "smoke del ensamblado", f"Falta smoke/smoke.py en: {', '.join(missing)}")
    ok, detail, env = _compose_up(cfg.out, "forge-ensamblado", 18999, "ensamblado")
    try:
        if not ok:
            return Gate(False, "docker compose up (ensamblado)", detail)
        time.sleep(3)
        bad = []
        for d, sc in scripts:
            code, out = run_cmd([sys.executable, str(sc)], cfg.out, timeout=900, env=env)
            if code:
                bad.append(f"[{d.slug}]\n{out}")
        return Gate(not bad, "smoke del ensamblado", "\n".join(bad) or f"{len(scripts)} escenarios pasan con todos los dominios juntos.")
    finally:
        run_cmd(["docker", "compose", "down", "-v"], cfg.out, timeout=300, env=env)


def design_gate(cfg: Config, rel: str) -> Gate:
    """El microfrontend debe usar el sistema de diseño del shell (tokens --mfe-* y vocabulario de clases) y no CSS suelto."""
    root = cfg.out / rel
    css = root / "src" / "styles.css"
    if not css.exists():
        return Gate(False, f"sistema de diseño ({rel})", f"Falta {css.relative_to(cfg.out)}.")
    text = css.read_text(encoding="utf-8", errors="ignore")
    problems = []
    if text.count("var(--mfe-") < 10:
        problems.append("styles.css casi no usa los tokens var(--mfe-*): el remote debe heredar el diseño del shell.")
    if len(re.findall(r"#[0-9a-fA-F]{3,8}\b", re.sub(r"var\(--mfe-[\w-]+,[^)]*\)", "", text))) > 0:
        problems.append("styles.css tiene colores fijos fuera de var(--mfe-…, respaldo): usa los tokens.")
    tsx = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in conformance._files(root / "src", {".tsx"}) if "__tests__" not in p.as_posix())
    for cls in ("card", "field"):
        if f'className="{cls}' not in tsx and f"className='{cls}" not in tsx and f"`{cls}" not in tsx:
            problems.append(f"Ningún componente usa la clase «{cls}» del sistema de diseño.")
    if "style={{" in tsx:
        problems.append("Hay estilos en línea (style={{…}}): muévelos al sistema de diseño.")
    return Gate(not problems, f"sistema de diseño ({rel})", "\n".join(problems) or "tokens y clases del sistema de diseño en uso.")


def shell_design_gate(cfg: Config) -> Gate:
    css = cfg.out / "frontend" / "mfe-shell" / "src" / "shell.css"
    ok = css.exists() and "--mfe-primary" in css.read_text(encoding="utf-8", errors="ignore")
    return Gate(ok, "sistema de diseño (shell)", "tokens --mfe-* definidos en el shell." if ok else "El shell no define los tokens --mfe-* (src/shell.css).")


def stubs_gate(cfg: Config, rel: str) -> Gate:
    """Falla si quedan marcas FORGE-STUB (esqueleto generado sin completar)."""
    root = cfg.out / rel
    left = [str(p.relative_to(cfg.out)) for p in conformance._files(root, {".ts", ".tsx"}) if "FORGE-STUB" in p.read_text(encoding="utf-8", errors="ignore")]
    return Gate(not left, f"sin esqueletos pendientes ({rel})", ("Completa y quita la marca FORGE-STUB en: " + ", ".join(left[:20])) if left else "ok")


# ------------------------------------------------------------------ Portafolio (reglas ENTRE dominios de la evaluación)
PLACEHOLDER = re.compile(r"^\s*(ejemplo|todo|tbd|x|n/?a|pendiente)\b", re.I)
MIN_ARGUMENT = 30


def weak_argument(text: str | None) -> bool:
    """¿La justificación es un borrador («Ejemplo: …», «TODO»…) o demasiado corta para ser un argumento?"""
    v = (text or "").strip()
    return len(v) < MIN_ARGUMENT or bool(PLACEHOLDER.match(v))


def portfolio_gates(cfg: Config, built: list, all_contexts: list[str]) -> list[Gate]:
    """Lo que la evaluación pide del CONJUNTO: 2 dominios reales, lenguajes distintos, arquitecturas mezcladas, argumentos
    reales (no los borradores «Ejemplo: …») y el resto de contextos simulados."""
    gates = []
    gates.append(Gate(len(built) >= 2, "evaluación: ≥ 2 dominios completos",
                      f"{len(built)} dominio(s) construido(s): {', '.join(d.context for d in built) or 'ninguno'}."))
    langs: dict[str, list[str]] = {}
    for d in built:
        langs.setdefault(d.language, []).append(d.context)
    dup = {l: c for l, c in langs.items() if len(c) > 1}
    gates.append(Gate(not dup, "evaluación: cada dominio en un lenguaje distinto",
                      ("; ".join(f"{l}: {', '.join(c)}" for l, c in dup.items()) + " comparten lenguaje.") if dup
                      else ", ".join(f"{d.context}={d.language}" for d in built)))
    archs = {d.architecture for d in built}
    gates.append(Gate(len(archs) >= 2 or len(built) < 2, "evaluación: arquitecturas mezcladas (clean-ddd y hexagonal)",
                      f"arquitecturas usadas: {', '.join(sorted(archs)) or 'ninguna'}."))
    weak = []
    for d in built:
        for k in ("lenguaje", "arquitectura", "estilo", "base_de_datos"):
            v = (d.rationale.get(k) or "").strip()
            if weak_argument(v):
                weak.append(f"{d.context}.{k}: «{v[:40]}» no es un argumento (borrador o demasiado corto; mín. {MIN_ARGUMENT} caracteres).")
    gates.append(Gate(not weak, "evaluación: decisiones argumentadas", "\n".join(weak) or "todas las decisiones tienen justificación propia."))
    sim = cfg.out / "simulators" / "simulators.json"
    real = {d.context for d in built}
    pending = [c for c in all_contexts if c not in real]
    try:
        data = json.loads(sim.read_text(encoding="utf-8"))
        simulated = {x["context"] for x in data.get("emits", []) + data.get("apis", [])}
    except (OSError, ValueError, KeyError):
        data, simulated = None, set()
    overlap = simulated & real
    gates.append(Gate(data is not None and (not pending or bool(simulated)) and not overlap, "evaluación: dominios restantes simulados",
                      "Falta out/simulators/simulators.json o está vacío." if data is None or (pending and not simulated)
                      else (f"Se simula un dominio que ya es real: {', '.join(sorted(overlap))}." if overlap
                            else f"{len(simulated)} contexto(s) simulado(s): {', '.join(sorted(simulated))}.")))
    return gates
