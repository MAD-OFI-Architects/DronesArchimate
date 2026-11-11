"""Reglas de negocio del agregado «Existencia» (códigos del contrato)."""
from __future__ import annotations


class ExistenciaInsuficiente:
    """EXISTENCIA_INSUFICIENTE: la cantidad pedida supera la existencia usable
    (física − reservada); el contrato exige ``reservado <= existencia``."""

    def __init__(self, solicitada: int, disponible: int) -> None:
        self._solicitada = solicitada
        self._disponible = disponible

    def es_rota(self) -> bool:
        return self._solicitada > self._disponible

    @property
    def mensaje(self) -> str:
        return (
            f"Existencia insuficiente: se necesitan {self._solicitada} y hay "
            f"{self._disponible} disponibles."
        )


class ReferenciaInexistente:
    """REFERENCIA_INEXISTENTE: la referencia del repuesto no existe en el
    catálogo o en las existencias del taller."""

    def __init__(self, referencia: str | None) -> None:
        self._referencia = referencia

    def es_rota(self) -> bool:
        return not self._referencia or not self._referencia.strip()

    @property
    def mensaje(self) -> str:
        return (
            f"La referencia '{self._referencia or '<vacía>'}' no existe en el "
            "catálogo de repuestos."
        )
