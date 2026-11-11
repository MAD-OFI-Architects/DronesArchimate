"""Puerta de SOLID (diapositiva 3): comprueba en el código real lo que se puede decidir de forma estática.

DIP (dominio/aplicación no dependen de lo concreto) ya lo cubren `arch_*`; aquí se añade la instanciación directa de
colaboradores concretos. El resto de principios se aproxima con señales objetivas y explicables:

- SRP: una clase de producción no debe crecer sin límite (líneas y métodos públicos).
- OCP: una cadena de preguntas por tipo (`isinstance`, `instanceof`, `GetType()`) obliga a editar el código para extender.
- LSP: un método sobrescrito que lanza «no soportado» rompe la sustituibilidad.
- ISP: un puerto con demasiados métodos fuerza a sus clientes a depender de lo que no usan.

Son heurísticas: detectan los olores graves, no prueban el principio. El revisor independiente (S50) cubre el criterio humano.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import conformance

MAX_CLASS_LINES = 300
MAX_PUBLIC_METHODS = 15
MAX_PORT_METHODS = 7
MAX_TYPE_TESTS = 3          # más de 3 preguntas por tipo en un archivo = cadena de if/switch por tipo

_EXT = {"python": {".py"}, "csharp": {".cs"}, "java": {".java"}}
_ABSTRACT_MARK = re.compile(r"abstractmethod|Protocol|\bABC\b|abstract\s")
_CONCRETE_COLLAB = r"(?:Repositor\w*|Publica\w*|Publisher\w*|Cifrad\w*|Cipher\w*|Encrypt\w*|Cache\w*|Gateway\w*|Adapter\w*|Client\w*)"

_UNSUPPORTED = {
    "python": re.compile(r"raise\s+NotImplementedError"),
    "csharp": re.compile(r"throw\s+new\s+(?:NotImplementedException|NotSupportedException)"),
    "java": re.compile(r"throw\s+new\s+(?:UnsupportedOperationException|NotImplementedError)"),
}
_TYPE_TEST = {
    # isinstance contra tipos primitivos es validación de entrada, no despacho por tipo de dominio: no cuenta.
    "python": re.compile(r"\bisinstance\s*\([^,()]+,(?!\s*\(?\s*(?:str|int|float|bool|bytes|list|dict|tuple|set|Decimal|datetime|date|UUID|Mapping|Sequence|type)\b)|\btype\s*\(\s*\w+\s*\)\s*(?:is|==)"),
    "csharp": re.compile(r"\.GetType\(\)\s*==|\bis\s+[A-Z]\w*\s+\w+\b"),
    "java": re.compile(r"\binstanceof\b|\.getClass\(\)\s*=="),
}
_CLASS = {
    "python": re.compile(r"^class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:", re.M),
    "csharp": re.compile(r"^\s*(?:public|internal)?\s*(?:sealed\s+|partial\s+|static\s+|abstract\s+)*(?:class|record)\s+(\w+)", re.M),
    "java": re.compile(r"^\s*(?:public\s+)?(?:final\s+|abstract\s+)*class\s+(\w+)", re.M),
}
_PUBLIC_METHOD = {
    "python": re.compile(r"^\s{4}(?:async\s+)?def\s+(?!_)\w+\s*\(", re.M),
    "csharp": re.compile(r"^\s*public\s+(?!class|record|sealed|static\s+class|enum|interface)[\w<>\[\],.?\s]+\s+\w+\s*\([^;{]*\)\s*(?:\{|=>)", re.M),
    "java": re.compile(r"^\s*public\s+(?!class|interface|enum|record)[\w<>\[\],.?\s]+\s+\w+\s*\([^;{]*\)\s*(?:throws\s+[\w,\s.]+)?\{", re.M),
}
_PORT = {
    "python": re.compile(r"^class\s+(\w+)\s*\(([^)]*(?:Protocol|ABC)[^)]*)\)\s*:", re.M),
    "csharp": re.compile(r"^\s*(?:public\s+)?interface\s+(I\w+)", re.M),
    "java": re.compile(r"^\s*(?:public\s+)?interface\s+(\w+)", re.M),
}
_PORT_METHOD = {
    "python": re.compile(r"^\s{4}(?:async\s+)?def\s+(?!_)\w+\s*\(", re.M),
    "csharp": re.compile(r"^\s*[\w<>\[\],.?]+\s+\w+\s*\([^)]*\)\s*;", re.M),
    "java": re.compile(r"^\s*(?:default\s+)?[\w<>\[\],.?]+\s+\w+\s*\([^)]*\)\s*(?:;|\{)", re.M),
}


@dataclass
class Finding:
    principle: str
    where: str
    why: str

    def __str__(self) -> str:
        return f"[{self.principle}] {self.where}: {self.why}"


def _is_test(rel: str) -> bool:
    low = "/" + rel.lower()
    return any(x in low for x in ("/tests/", "/test/", ".tests/", "/smoke/")) or rel.lower().endswith(("test.cs", "tests.cs", "test.java", "_test.py"))


def _layer(rel: str) -> str:
    low = "/" + rel.lower()
    for name in ("domain", "application", "contracts", "infrastructure", "adapters", "api"):
        if f"/{name}/" in low or f".{name}/" in low:
            return name
    return ""


def _block(text: str, start: int, language: str) -> str:
    """Cuerpo aproximado de una declaración: hasta la siguiente declaración del mismo nivel."""
    if language == "python":
        m = re.compile(r"^\S", re.M).search(text, text.index("\n", start) + 1 if "\n" in text[start:] else len(text))
        return text[start:m.start() if m else len(text)]
    depth, i, opened = 0, text.find("{", start), False
    if i < 0:
        return text[start:start + 1]
    for j in range(i, len(text)):
        if text[j] == "{":
            depth, opened = depth + 1, True
        elif text[j] == "}":
            depth -= 1
            if opened and depth == 0:
                return text[start:j + 1]
    return text[start:]


def scan(root: Path, language: str) -> list[Finding]:
    out: list[Finding] = []
    exts = _EXT[language]
    for f in conformance._files(root, exts):
        rel = f.relative_to(root).as_posix()
        if _is_test(rel):
            continue
        layer = _layer(rel)
        text = f.read_text(encoding="utf-8", errors="ignore")

        # SRP — tamaño de clase y métodos públicos
        for m in _CLASS[language].finditer(text):
            body = _block(text, m.start(), language)
            lines = body.count("\n") + 1
            # las propiedades (@property) son acceso al estado, no comportamiento: no cuentan como métodos públicos
            pub = len(_PUBLIC_METHOD[language].findall(re.sub(r"@\w*property\w*\s*\n\s*(?:async\s+)?def\s+\w+", "", body)))
            if lines > MAX_CLASS_LINES:
                out.append(Finding("SRP", f"{rel}", f"la clase «{m.group(1)}» tiene {lines} líneas (máx. {MAX_CLASS_LINES}); probablemente hace más de una cosa."))
            elif pub > MAX_PUBLIC_METHODS:
                out.append(Finding("SRP", f"{rel}", f"la clase «{m.group(1)}» expone {pub} métodos públicos (máx. {MAX_PUBLIC_METHODS}); sepárala por responsabilidad."))

        # OCP — cadenas de preguntas por tipo
        tests = len(_TYPE_TEST[language].findall(text))
        if tests > MAX_TYPE_TESTS:
            out.append(Finding("OCP", rel, f"{tests} preguntas por tipo (isinstance/instanceof/GetType); usa polimorfismo, estrategia o state en vez de una cadena."))

        # LSP — métodos que declaran «no soportado»
        for m in _UNSUPPORTED[language].finditer(text):
            ctx = text[max(0, m.start() - 200):m.start()]
            if language == "python" and _ABSTRACT_MARK.search(ctx):
                continue
            out.append(Finding("LSP", rel, "lanza «no soportado/no implementado» en un método: un subtipo debe poder sustituir a su tipo base."))
            break

        # ISP — puertos demasiado anchos
        for m in _PORT[language].finditer(text):
            body = _block(text, m.start(), language)
            n = len(_PORT_METHOD[language].findall(body))
            if n > MAX_PORT_METHODS:
                out.append(Finding("ISP", rel, f"el puerto «{m.group(1)}» declara {n} métodos (máx. {MAX_PORT_METHODS}); divídelo en interfaces por cliente."))

        # DIP — dominio y aplicación no construyen colaboradores concretos
        if layer in ("domain", "application"):
            ctor = (re.compile(rf"\b(?!I[A-Z])({_CONCRETE_COLLAB})\s*\(") if language == "python"
                    else re.compile(rf"\bnew\s+({_CONCRETE_COLLAB})\s*[(<]"))
            for m in ctor.finditer(text):
                line = text[:m.start()].count("\n") + 1
                ctx = text[max(0, text.rfind("\n", 0, m.start())):m.start()]
                if language == "python" and re.search(r"(?:class|def|import|from)\s", ctx):
                    continue
                out.append(Finding("DIP", f"{rel}:{line}", f"la capa {layer} instancia «{m.group(1)}» directamente; recíbelo por constructor como abstracción."))
    return out
