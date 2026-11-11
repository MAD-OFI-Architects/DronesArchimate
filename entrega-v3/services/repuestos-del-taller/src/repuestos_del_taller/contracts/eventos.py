"""Eventos publicados en el bus: solo primitivos, sin referencias a otras capas."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FaltanteDetectadoV1:
    event_id: str
    occurred_on: str
    parada_id: str
    referencia: str
    cantidad_faltante: int

    def a_payload(self) -> dict[str, object]:
        """Carga útil del sobre según `contrato-bus.md`; `eventId` es la clave de idempotencia."""
        return {
            "eventId": self.event_id,
            "paradaId": self.parada_id,
            "referencia": self.referencia,
            "cantidadFaltante": self.cantidad_faltante,
        }
