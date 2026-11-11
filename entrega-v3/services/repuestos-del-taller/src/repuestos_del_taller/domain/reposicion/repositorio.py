"""Puerto del agregado «Solicitud de reposición»: persistencia sin dependencias."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from .solicitud_de_reposicion import SolicitudDeReposicion


class ISolicitudDeReposicionRepository(ABC):
    """Puerto de persistencia de solicitudes de reposición, en lenguaje ubicuo."""

    @abstractmethod
    def por_id(self, id_: uuid.UUID) -> SolicitudDeReposicion | None:
        """Devuelve la solicitud por su identificador o None si no existe."""

    @abstractmethod
    def abierta_de_referencia(self, referencia: str) -> SolicitudDeReposicion | None:
        """Devuelve la solicitud abierta de la referencia o None si no hay."""

    @abstractmethod
    def guardar(self, solicitud: SolicitudDeReposicion) -> None:
        """Guarda la solicitud con sus eventos pendientes."""
