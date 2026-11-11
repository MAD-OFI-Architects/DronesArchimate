"""Traducción de eventos de dominio a los contratos publicados."""
from __future__ import annotations

from ..contracts.eventos import FaltanteDetectadoV1
from ..domain.existencias.eventos import FaltanteDetectado


class FaltanteDetectadoTraductor:
    def traducir(self, evento: FaltanteDetectado) -> FaltanteDetectadoV1:
        return FaltanteDetectadoV1(
            event_id=str(evento.evento_id), occurred_on=evento.ocurrio_en.isoformat(),
            parada_id=evento.orden_trabajo_id, referencia=evento.referencia,
            cantidad_faltante=max(0, evento.solicitada - evento.disponible),
        )
