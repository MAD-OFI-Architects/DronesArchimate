"""Patrón State: ciclo de vida de la solicitud de reposición con transiciones
validadas. Abierta → aprobada o cancelada; los estados terminales son
inmutables (no admiten más transiciones).
"""
from __future__ import annotations

from ..compartido.errores import ErrorDeDominio

ABIERTA = "abierta"
APROBADA = "aprobada"
CANCELADA = "cancelada"


class EstadoSolicitud:
    """Estado de la solicitud: valida las transiciones que permite."""

    NOMBRE: str = ""
    PERMITIDAS: frozenset[str] = frozenset()

    def nombre(self) -> str:
        return self.NOMBRE

    def transitar_a(self, destino: "EstadoSolicitud") -> "EstadoSolicitud":
        if destino.NOMBRE == self.NOMBRE:
            return self
        if destino.NOMBRE not in self.PERMITIDAS:
            raise ErrorDeDominio(
                f"La solicitud en estado '{self.NOMBRE}' no puede pasar a "
                f"'{destino.NOMBRE}'."
            )
        return destino


class Abierta(EstadoSolicitud):
    NOMBRE = ABIERTA
    PERMITIDAS = frozenset({APROBADA, CANCELADA})


class Aprobada(EstadoSolicitud):
    NOMBRE = APROBADA
    PERMITIDAS = frozenset()


class Cancelada(EstadoSolicitud):
    NOMBRE = CANCELADA
    PERMITIDAS = frozenset()


ESTADOS_POR_NOMBRE: dict[str, EstadoSolicitud] = {
    ABIERTA: Abierta(),
    APROBADA: Aprobada(),
    CANCELADA: Cancelada(),
}


def estado_por_nombre(nombre: str) -> EstadoSolicitud:
    estado = ESTADOS_POR_NOMBRE.get(nombre)
    if estado is None:
        raise ErrorDeDominio(f"'{nombre}' no es un estado de la solicitud.")
    return estado
