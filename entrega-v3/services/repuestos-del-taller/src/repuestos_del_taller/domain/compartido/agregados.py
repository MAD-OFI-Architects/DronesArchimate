"""Entidades y raíz de agregado.

- ``Entidad``: objetos que se distinguen por su Id y no por sus datos.
- ``RaizDeAgregado``: única puerta para cambiar el agregado; guarda los eventos
  de lo que le ocurre con ``levantar``.
- ``IOriginador``: contrato del patrón Memento: el agregado entrega una
  instantánea de primitivos y se reconstruye desde ella validando
  (``restaurar_desde``, método de clase del agregado concreto).
"""
from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from .eventos import EventoDeDominio

TId = TypeVar("TId")
TMemento = TypeVar("TMemento")


class Entidad(Generic[TId]):
    """Base de los objetos con identidad propia."""

    def __init__(self, id_: TId) -> None:
        self._id = id_

    @property
    def id(self) -> TId:
        return self._id

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, type(self)) and self._id == otro._id

    def __hash__(self) -> int:
        return hash((type(self).__name__, str(self._id)))


class RaizDeAgregado(Entidad[TId]):
    """Raíz de un agregado: colecciona los eventos de dominio que levanta."""

    def __init__(self, id_: TId) -> None:
        super().__init__(id_)
        self._eventos: list[EventoDeDominio] = []

    @property
    def eventos(self) -> tuple[EventoDeDominio, ...]:
        return tuple(self._eventos)

    def limpiar_eventos(self) -> None:
        self._eventos.clear()

    def levantar(self, evento: EventoDeDominio) -> None:
        self._eventos.append(evento)


class IOriginador(Protocol[TMemento]):
    """Contrato Memento: crear la instantánea y restaurarse desde ella."""

    def crear_memento(self) -> TMemento: ...
