"""Reglas de negocio con nombre propio del lenguaje ubicuo.

Cada regla es una clase con nombre del lenguaje ubicuo; si se incumple,
:func:`verificar_regla` lanza :class:`ViolacionDeReglaDeNegocio` y la API
responde 422 indicando cuál fue.
"""
from __future__ import annotations

from typing import Protocol

from .errores import ViolacionDeReglaDeNegocio


class ReglaDeNegocio(Protocol):
    """Contrato de una regla de negocio: sabe decir si está rota y por qué."""

    @property
    def mensaje(self) -> str: ...

    def es_rota(self) -> bool: ...


def verificar_regla(regla: ReglaDeNegocio) -> None:
    """Lanza ``ViolacionDeReglaDeNegocio`` si la regla está rota."""
    if regla.es_rota():
        raise ViolacionDeReglaDeNegocio(regla)
