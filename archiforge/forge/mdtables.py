"""Lectura mínima de las tablas Markdown del repositorio (contratos, mapa de contextos)."""
from __future__ import annotations

import re
from pathlib import Path


def tables(text: str) -> list[list[list[str]]]:
    """Devuelve cada tabla como lista de filas (sin la fila separadora)."""
    out, cur = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            cur.append(cells)
        else:
            if cur:
                out.append(cur)
                cur = []
    if cur:
        out.append(cur)
    return out


def sections(text: str, level: int = 3) -> dict[str, str]:
    """Parte el documento por encabezados '### Título' y devuelve {título: cuerpo}."""
    marker = "#" * level + " "
    result: dict[str, str] = {}
    title, buf = None, []
    for line in text.splitlines():
        if line.startswith(marker):
            if title is not None:
                result[title] = "\n".join(buf)
            title, buf = line[len(marker):].strip(), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        result[title] = "\n".join(buf)
    return result


def key_value_table(body: str) -> dict[str, str]:
    """Tabla de dos columnas 'Campo | Contenido' -> dict."""
    result: dict[str, str] = {}
    for t in tables(body):
        for row in t:
            if len(row) >= 2 and row[0].lower() != "campo":
                result[row[0]] = row[1]
    return result


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""
