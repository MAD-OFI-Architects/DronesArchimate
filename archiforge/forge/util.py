"""Utilidades de nombres: el modelo está en español con tildes; el código no."""
from __future__ import annotations

import re
import unicodedata


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def words(text: str) -> list[str]:
    return [w for w in re.split(r"[^A-Za-z0-9]+", strip_accents(text)) if w]


def pascal(text: str) -> str:
    """'Orden de trabajo' -> 'OrdenDeTrabajo'; 'Consumo (de repuesto)' -> 'ConsumoDeRepuesto'."""
    return "".join(w[:1].upper() + w[1:] for w in words(text))


def snake(text: str) -> str:
    return "_".join(w.lower() for w in words(text))


def kebab(text: str) -> str:
    return "-".join(w.lower() for w in words(text))


def norm(text: str) -> str:
    """Forma comparable: sin tildes, minúsculas, solo alfanuméricos."""
    return re.sub(r"[^a-z0-9]", "", strip_accents(text).lower())


def infinitive_to_noun_phrase(text: str) -> str:
    return pascal(text)
