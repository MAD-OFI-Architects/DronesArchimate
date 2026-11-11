"""Puerto del agregado «Existencia»: persistencia sin dependencias externas."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .existencia import Existencia


class IExistenciaRepository(ABC):
    """Puerto de persistencia de existencias, en lenguaje ubicuo."""

    @abstractmethod
    def por_referencia(self, referencia: str) -> Existencia | None:
        """Devuelve la existencia de la referencia o None si no existe."""

    @abstractmethod
    def guardar(self, existencia: Existencia) -> None:
        """Guarda la existencia con sus reservas y eventos pendientes."""
