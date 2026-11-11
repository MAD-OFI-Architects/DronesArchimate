"""Objetos de valor del agregado «Existencia»: inmutables y validados con Guard."""
from __future__ import annotations

from dataclasses import dataclass

from ..compartido.guard import Guard


@dataclass(frozen=True, slots=True)
class Cantidad:
    """Unidades de un repuesto: física, reservada y disponible."""

    valor: int

    def __post_init__(self) -> None:
        Guard.no_nulo(self.valor, "cantidad")
        Guard.no_negativo(self.valor, "cantidad")

    def sumar(self, otra: "Cantidad") -> "Cantidad":
        return Cantidad(self.valor + otra.valor)


@dataclass(frozen=True, slots=True)
class StockMinimo:
    """Cantidad por debajo de la cual se solicita reposición inmediata."""

    valor: int

    def __post_init__(self) -> None:
        Guard.no_nulo(self.valor, "stock mínimo")
        Guard.no_negativo(self.valor, "stock mínimo")


@dataclass(frozen=True, slots=True)
class PlazoDeEntrega:
    """Tiempo que tarda un repuesto en llegar: 1 a 3 días con el distribuidor,
    2 a 6 semanas si se importa."""

    dias: int

    def __post_init__(self) -> None:
        Guard.no_nulo(self.dias, "plazo de entrega")
        Guard.en_rango(self.dias, 1, 42, "plazo de entrega")
