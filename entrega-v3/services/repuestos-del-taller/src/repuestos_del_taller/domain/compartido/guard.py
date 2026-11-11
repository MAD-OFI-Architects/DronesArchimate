"""Guard: validaciones centralizadas que usan los constructores y métodos del
dominio para rechazar datos inválidos sin repetir el mismo ``if`` (DRY).

Un dato inválido levanta :class:`ErrorDeDominio`.
"""
from __future__ import annotations

import uuid

from .errores import ErrorDeDominio


class Guard:
    """Clase estática de validaciones del dominio."""

    @staticmethod
    def no_nulo(valor: object, campo: str) -> object:
        if valor is None:
            raise ErrorDeDominio(f"El campo '{campo}' es obligatorio.")
        return valor

    @staticmethod
    def texto(valor: object, campo: str, longitud_maxima: int = 250) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorDeDominio(f"El campo '{campo}' debe ser un texto no vacío.")
        limpio = valor.strip()
        if len(limpio) > longitud_maxima:
            raise ErrorDeDominio(
                f"El campo '{campo}' no puede exceder {longitud_maxima} caracteres."
            )
        return limpio

    @staticmethod
    def positivo(valor: object, campo: str) -> int:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ErrorDeDominio(f"El campo '{campo}' debe ser mayor que cero.")
        return valor

    @staticmethod
    def no_negativo(valor: object, campo: str) -> int:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
            raise ErrorDeDominio(f"El campo '{campo}' no puede ser negativo.")
        return valor

    @staticmethod
    def en_rango(valor: object, minimo: int, maximo: int, campo: str) -> int:
        if not isinstance(valor, int) or isinstance(valor, bool) or not minimo <= valor <= maximo:
            raise ErrorDeDominio(
                f"El campo '{campo}' debe estar entre {minimo} y {maximo}."
            )
        return valor

    @staticmethod
    def no_vacio(valor: object, campo: str) -> uuid.UUID:
        if not isinstance(valor, uuid.UUID) or valor == uuid.UUID(int=0):
            raise ErrorDeDominio(f"El campo '{campo}' debe ser un identificador válido.")
        return valor
