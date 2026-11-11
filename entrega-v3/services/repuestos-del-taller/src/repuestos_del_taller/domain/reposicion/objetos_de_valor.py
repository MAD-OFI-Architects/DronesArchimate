"""Objetos de valor del agregado «Solicitud de reposición»."""
from __future__ import annotations

from dataclasses import dataclass

from ..compartido.errores import ErrorDeDominio
from ..compartido.guard import Guard


@dataclass(frozen=True, slots=True)
class CantidadSolicitada:
    """Unidades pedidas en una solicitud de reposición."""

    valor: int

    def __post_init__(self) -> None:
        Guard.no_nulo(self.valor, "cantidad solicitada")
        Guard.positivo(self.valor, "cantidad solicitada")


class NivelDeAprobacion:
    """Quién debe aprobar una solicitud según su monto: jefe hasta $5 millones,
    gerencia por encima."""

    JEFE = "jefe"
    GERENCIA = "gerencia"
    UMBRAL_JEFE = 5_000_000

    __slots__ = ("_valor",)

    def __init__(self, valor: str) -> None:
        if valor not in (self.JEFE, self.GERENCIA):
            raise ErrorDeDominio(
                f"'{valor}' no es un nivel de aprobación válido."
            )
        self._valor = valor

    @classmethod
    def por_monto(cls, monto: int) -> "NivelDeAprobacion":
        Guard.no_negativo(monto, "monto")
        return cls(cls.GERENCIA if monto > cls.UMBRAL_JEFE else cls.JEFE)

    @property
    def valor(self) -> str:
        return self._valor

    @property
    def requiere_gerencia(self) -> bool:
        return self._valor == self.GERENCIA

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, NivelDeAprobacion) and self._valor == otro._valor

    def __hash__(self) -> int:
        return hash(self._valor)

    def __repr__(self) -> str:
        return f"NivelDeAprobacion({self._valor!r})"
