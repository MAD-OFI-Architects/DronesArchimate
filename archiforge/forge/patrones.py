"""Comprobación ESTRUCTURAL de los patrones que el arquitecto eligió, sobre el código generado (C#, Python y Java).

Cada patrón del catálogo declara `chequeo = [...]`: qué forma debe existir en el código. Son heurísticas sobre declaraciones (no un análisis
semántico): detectan que la estructura exista, no que el patrón esté bien aplicado. Complementan al ADR (que cita las clases reales) y al
gate de cableado (que exige que lo definido se use).

Chequeos:
  abstraccion_con_implementaciones:N  una interfaz o clase abstracta con al menos N implementaciones concretas
  envoltorio                          una clase que implementa X y mantiene una referencia a X (decorador, proxy, composite, cadena)
  instancia_unica                     constructor privado + acceso estático a la instancia
  constructor_fluido                  métodos encadenados que devuelven la propia instancia + un método de construcción
  clonacion                           un método de copia/clonación
  suscriptores                        suscribir + notificar sobre una colección de interesados
  plantilla                           clase abstracta cuyo método concreto invoca un paso abstracto
  clase_con_nombre:<regex>            alguna clase cuyo nombre cumple la expresión (rol nombrado por convención)
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import conformance, solid

_EXT = {"csharp": {".cs"}, "python": {".py"}, "java": {".java"}}


@dataclass
class Decl:
    name: str
    kind: str                  # interface | abstract | class
    bases: set[str] = field(default_factory=set)
    body: str = ""
    file: str = ""


def _base_names(raw: str) -> set[str]:
    out = set()
    for part in re.split(r",", re.sub(r"<[^<>]*>|\[[^\[\]]*\]", "", raw or "")):
        part = re.sub(r"\b(extends|implements|where|public|new|metaclass\s*=\s*\w+)\b", " ", part).strip().split()
        if part:
            out.add(part[-1].split(".")[-1].strip("(){}:;"))
    return {x for x in out if x and x not in ("object", "Object", "class", "struct")}


_CS = re.compile(r"^[ \t]*((?:(?:public|internal|private|protected|static|sealed|partial|abstract|readonly|unsafe)\s+)*)(interface|class|record|struct)\s+(\w+)"
                 r"(?:<[^>\n]*>)?(?:\s*\([^)]*\))?[ \t]*(?::\s*([^{\n;]+))?", re.M)
_JAVA = re.compile(r"^[ \t]*((?:(?:public|protected|private|static|final|abstract|sealed)\s+)*)(interface|class|record)\s+(\w+)(?:<[^>\n]*>)?([^{;\n]*)", re.M)
_PY = re.compile(r"^class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:", re.M)


def declarations(root: Path, language: str) -> list[Decl]:
    out: list[Decl] = []
    for f in conformance._files(root, _EXT[language]):
        rel = f.relative_to(root).as_posix()
        low = "/" + rel.lower()
        if any(x in low for x in ("/tests/", "/test/", ".tests/", "/smoke/")):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        if language == "python":
            for m in _PY.finditer(text):
                body = solid._block(text, m.start(), "python")
                bases = _base_names(m.group(2))
                abstract = bool(bases & {"ABC", "Protocol"}) or "@abstractmethod" in body
                kind = "interface" if "Protocol" in bases else "abstract" if abstract else "class"      # ABC con métodos concretos = clase abstracta
                out.append(Decl(m.group(1), kind, bases - {"ABC", "Protocol"}, body, rel))
        else:
            rx = _CS if language == "csharp" else _JAVA
            for m in rx.finditer(text):
                mods, kw, name = m.group(1) or "", m.group(2), m.group(3)
                bases = _base_names(m.group(4))
                kind = "interface" if kw == "interface" else "abstract" if "abstract" in mods else "class"
                out.append(Decl(name, kind, bases, solid._block(text, m.start(), language), rel))
    return out


def _after_header(d: Decl, language: str) -> str:
    cut = d.body.find(":\n") + 2 if language == "python" else d.body.find("{") + 1
    return d.body[max(cut, 0):]


# ---------------------------------------------------------------- chequeos: (decls, lenguaje, argumento) -> (ok, detalle)
def _abstraccion(decls, language, arg):
    n = int(arg or 2)
    abstract = {d.name for d in decls if d.kind in ("interface", "abstract")}
    count: dict[str, int] = defaultdict(int)
    for d in decls:
        if d.kind == "class":
            for b in d.bases & abstract:
                count[b] += 1
    best = max(count.items(), key=lambda x: x[1], default=("", 0))
    return best[1] >= n, (f"mejor candidato «{best[0]}» con {best[1]} implementación(es)" if best[0] else "no hay una interfaz o clase abstracta con implementaciones") + f"; se exigen {n}"


def _envoltorio(decls, language, arg):
    names = {d.name for d in decls}
    for d in decls:
        if d.kind != "class":
            continue
        inner = _after_header(d, language)
        for b in d.bases & names:
            if re.search(rf"\b{re.escape(b)}\b", inner):
                return True, f"«{d.name}» implementa y envuelve «{b}»"
    return False, "ninguna clase implementa una interfaz y mantiene a la vez una referencia a ella"


def _instancia_unica(decls, language, arg):
    for d in decls:
        b = d.body
        if language == "python":
            ok = "__new__" in b and re.search(r"\b_?(instance|instancia)\b|cls\._", b)
        elif language == "csharp":
            ok = re.search(r"\bprivate\s+" + re.escape(d.name) + r"\s*\(\s*\)", b) and re.search(r"\bstatic\b[^;{(]*\b(Instance|Instancia|Current|Default)\b", b)
        else:
            ok = re.search(r"\bprivate\s+" + re.escape(d.name) + r"\s*\(\s*\)", b) and re.search(r"\bstatic\b[^;{(]*\b(instance|INSTANCE|instancia)\b|getInstance\s*\(", b)
        if ok:
            return True, f"«{d.name}»"
    return False, "ninguna clase tiene constructor privado y acceso estático a su única instancia"


def _constructor_fluido(decls, language, arg):
    ret = r"return\s+self\b" if language == "python" else r"return\s+this\s*;"
    for d in decls:
        if len(re.findall(ret, d.body)) >= 2 and re.search(r"\b(Build|build|Construir|construir)\s*\(", d.body):
            return True, f"«{d.name}»"
    return False, "ninguna clase encadena métodos (devuelve la propia instancia) y termina en un método de construcción"


def _clonacion(decls, language, arg):
    for d in decls:
        if re.search(r"\b(Clone|clone|Clonar|clonar|Copiar|copiar|copy|deepcopy|__copy__|MemberwiseClone)\s*\(|def __copy__", d.body):
            return True, f"«{d.name}»"
    return False, "ninguna clase ofrece un método de copia o clonación"


def _suscriptores(decls, language, arg):
    for d in decls:
        b = d.body
        if (re.search(r"\b(Subscribe|subscribe|Suscribir|suscribir|Attach|attach|add_observer|AddObserver|add_listener|AddListener|agregar_observador)\w*\s*\(", b)
                and re.search(r"\b(Notify|notify|Notificar|notificar|emit|Emit|publish|Publish)\w*\s*\(", b)
                and re.search(r"List|list|Set|set\(|\[\]|Collection|Dictionary|dict", b)):
            return True, f"«{d.name}»"
    return False, "ninguna clase mantiene una colección de suscriptores con operaciones de suscribir y notificar"


def _plantilla(decls, language, arg):
    for d in decls:
        if d.kind != "abstract":
            continue
        if language == "python":
            steps = set(re.findall(r"@abstractmethod\s*\n\s*(?:async\s+)?def\s+(\w+)", d.body))
        else:
            steps = set(re.findall(r"\babstract\s+[\w<>\[\],.? ]+?\s+(\w+)\s*\(", d.body))
        for s in steps:
            if len(re.findall(rf"\b{re.escape(s)}\s*\(", d.body)) >= 2:       # la declaración + al menos una llamada desde un método concreto
                return True, f"«{d.name}» invoca el paso abstracto «{s}»"
    return False, "ninguna clase abstracta tiene un método concreto que invoque uno de sus pasos abstractos"


def _nombre(decls, language, arg):
    rx = re.compile(arg or ".")
    hit = [d.name for d in decls if rx.search(d.name)]
    return bool(hit), (f"«{hit[0]}»" if hit else f"ninguna clase cuyo nombre cumpla {arg}")


CHECKS = {"abstraccion_con_implementaciones": _abstraccion, "envoltorio": _envoltorio, "instancia_unica": _instancia_unica,
          "constructor_fluido": _constructor_fluido, "clonacion": _clonacion, "suscriptores": _suscriptores, "plantilla": _plantilla,
          "clase_con_nombre": _nombre}


def parse_check(spec: str):
    """`nombre[:argumento]` -> (nombre, argumento) o None si el chequeo no existe."""
    name, _, arg = spec.partition(":")
    return (name, arg or None) if name in CHECKS else None


def run_check(spec: str, decls: list[Decl], language: str) -> tuple[bool, str]:
    parsed = parse_check(spec)
    if parsed is None:
        return False, f"chequeo desconocido «{spec}»"
    return CHECKS[parsed[0]](decls, language, parsed[1])
