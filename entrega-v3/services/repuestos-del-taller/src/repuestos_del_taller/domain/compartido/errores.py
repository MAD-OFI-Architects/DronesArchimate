"""Errores del dominio.

`ErrorDeDominio`: un dato no es válido para el negocio (la API responde 400).
`ViolacionDeReglaDeNegocio`: se rompió una regla con nombre propio del lenguaje
ubicuo (la API responde 422 indicando cuál fue).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .reglas import ReglaDeNegocio


class ErrorDeDominio(Exception):
    """El dato que llega es inválido para el negocio."""


class ViolacionDeReglaDeNegocio(ErrorDeDominio):
    """Una regla de negocio con nombre propio quedó rota."""

    def __init__(self, regla: ReglaDeNegocio) -> None:
        self.regla = regla
        super().__init__(regla.mensaje)
