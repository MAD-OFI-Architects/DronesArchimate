"""Patrón State: ciclo de vida de la existencia con transiciones validadas.

disponible → reservado → consumido → bajo mínimo → reponiendo.
Un comando solo procede si el estado actual lo permite; una transición no
permitida levanta ``ErrorDeDominio``.
"""
from __future__ import annotations

from ..compartido.errores import ErrorDeDominio

DISPONIBLE = "disponible"
RESERVADO = "reservado"
CONSUMIDO = "consumido"
BAJO_MINIMO = "bajo_minimo"
REPONIENDO = "reponiendo"


class EstadoExistencia:
    """Estado del ciclo de vida: valida las transiciones que permite."""

    NOMBRE: str = ""
    PERMITIDAS: frozenset[str] = frozenset()

    def nombre(self) -> str:
        return self.NOMBRE

    def transitar_a(self, destino: "EstadoExistencia") -> "EstadoExistencia":
        if destino.NOMBRE == self.NOMBRE:
            return self
        if destino.NOMBRE not in self.PERMITIDAS:
            raise ErrorDeDominio(
                f"La existencia en estado '{self.NOMBRE}' no puede pasar a "
                f"'{destino.NOMBRE}'."
            )
        return destino


class Disponible(EstadoExistencia):
    NOMBRE = DISPONIBLE
    PERMITIDAS = frozenset({RESERVADO})


class Reservado(EstadoExistencia):
    NOMBRE = RESERVADO
    PERMITIDAS = frozenset({DISPONIBLE, CONSUMIDO})


class Consumido(EstadoExistencia):
    NOMBRE = CONSUMIDO
    PERMITIDAS = frozenset({BAJO_MINIMO, DISPONIBLE, RESERVADO})


class BajoMinimo(EstadoExistencia):
    NOMBRE = BAJO_MINIMO
    PERMITIDAS = frozenset({REPONIENDO, DISPONIBLE, RESERVADO, CONSUMIDO})


class Reponiendo(EstadoExistencia):
    NOMBRE = REPONIENDO
    PERMITIDAS = frozenset({DISPONIBLE, RESERVADO, CONSUMIDO})


ESTADOS_POR_NOMBRE: dict[str, EstadoExistencia] = {
    DISPONIBLE: Disponible(),
    RESERVADO: Reservado(),
    CONSUMIDO: Consumido(),
    BAJO_MINIMO: BajoMinimo(),
    REPONIENDO: Reponiendo(),
}


def estado_por_nombre(nombre: str) -> EstadoExistencia:
    estado = ESTADOS_POR_NOMBRE.get(nombre)
    if estado is None:
        raise ErrorDeDominio(f"'{nombre}' no es un estado del ciclo de vida.")
    return estado
