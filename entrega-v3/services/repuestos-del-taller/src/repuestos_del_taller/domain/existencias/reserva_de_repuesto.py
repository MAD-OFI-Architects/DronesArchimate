"""Entidad interna «Reserva de repuesto»: apartado de repuestos para una
intervención programada (identificada por la orden de trabajo).
"""
from __future__ import annotations

import uuid

from ..compartido.agregados import Entidad
from ..compartido.guard import Guard
from .objetos_de_valor import Cantidad


class ReservaDeRepuesto(Entidad[uuid.UUID]):
    """Reserva de una cantidad de la referencia para una orden de trabajo."""

    def __init__(
        self, id_: uuid.UUID, orden_trabajo_id: str, cantidad: Cantidad
    ) -> None:
        super().__init__(Guard.no_vacio(id_, "id de la reserva"))
        self._orden_trabajo_id = Guard.texto(orden_trabajo_id, "orden de trabajo")
        Guard.no_nulo(cantidad, "cantidad reservada")
        self._cantidad = cantidad

    @property
    def orden_trabajo_id(self) -> str:
        return self._orden_trabajo_id

    @property
    def cantidad(self) -> Cantidad:
        return self._cantidad
