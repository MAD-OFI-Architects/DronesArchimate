from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FaltanteDetectadoV1:
    event_id: str
    occurred_on: str
    parada_id: str
    referencia: str
    cantidad_faltante: int
