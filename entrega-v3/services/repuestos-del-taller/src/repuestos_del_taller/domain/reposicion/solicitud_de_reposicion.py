"""Raíz del agregado «Solicitud de reposición»: pedido interno que nace al
tocar el stock mínimo. Un método de negocio por comando del modelo; cada
comando valida sus reglas y levanta su evento de dominio.
"""
from __future__ import annotations

import uuid

from ..compartido.agregados import RaizDeAgregado
from ..compartido.guard import Guard
from ..compartido.reglas import verificar_regla
from .estados import Abierta, Aprobada, Cancelada, EstadoSolicitud, estado_por_nombre
from .eventos import ReposicionSolicitada, SolicitudAprobada, SolicitudCancelada
from .memento import SolicitudDeReposicionMemento
from .objetos_de_valor import CantidadSolicitada, NivelDeAprobacion
from .reglas import SolicitudAbierta


class SolicitudDeReposicion(RaizDeAgregado[uuid.UUID]):
    """Solicitud de reposición de una referencia, con su monto y nivel."""

    def __init__(
        self,
        id_: uuid.UUID,
        referencia: str,
        cantidad_solicitada: CantidadSolicitada,
        monto: int,
        nivel: NivelDeAprobacion | None = None,
        estado: EstadoSolicitud | None = None,
    ) -> None:
        super().__init__(Guard.no_vacio(id_, "id de la solicitud"))
        self._referencia = Guard.texto(referencia, "referencia")
        Guard.no_nulo(cantidad_solicitada, "cantidad solicitada")
        self._cantidad = cantidad_solicitada
        self._monto = Guard.no_negativo(monto, "monto")
        self._nivel = nivel if nivel is not None else NivelDeAprobacion.por_monto(monto)
        self._estado = estado if estado is not None else Abierta()

    # -- comandos del modelo -------------------------------------------------

    @classmethod
    def solicitar(
        cls,
        id_: uuid.UUID,
        referencia: str,
        cantidad_solicitada: CantidadSolicitada,
        monto: int,
        hay_abierta: bool,
    ) -> "SolicitudDeReposicion":
        """Solicitar reposición → ReposicionSolicitada.

        ``hay_abierta`` lo resuelve la aplicación consultando el repositorio
        (una solicitud abierta por referencia); el agregado verifica la regla.
        """
        verificar_regla(SolicitudAbierta(hay_abierta, referencia))
        solicitud = cls(id_, referencia, cantidad_solicitada, monto)
        solicitud.levantar(
            ReposicionSolicitada(
                solicitud_id=str(solicitud.id),
                referencia=solicitud.referencia,
                cantidad=solicitud.cantidad.valor,
                nivel=solicitud._nivel.valor,
            )
        )
        return solicitud

    def aprobar(self) -> None:
        """Aprobar solicitud → SolicitudAprobada (solo estando abierta)."""
        self._estado = self._estado.transitar_a(Aprobada())
        self.levantar(
            SolicitudAprobada(
                solicitud_id=str(self.id),
                referencia=self._referencia,
                nivel=self._nivel.valor,
            )
        )

    def cancelar(self) -> None:
        """Cancelar solicitud → SolicitudCancelada (solo estando abierta)."""
        self._estado = self._estado.transitar_a(Cancelada())
        self.levantar(
            SolicitudCancelada(
                solicitud_id=str(self.id),
                referencia=self._referencia,
            )
        )

    # -- memento -------------------------------------------------------------

    def crear_memento(self) -> SolicitudDeReposicionMemento:
        return SolicitudDeReposicionMemento(
            id=str(self.id),
            referencia=self._referencia,
            cantidad_solicitada=self._cantidad.valor,
            monto=self._monto,
            nivel=self._nivel.valor,
            estado=self._estado.nombre(),
        )

    @classmethod
    def restaurar_desde(cls, memento: SolicitudDeReposicionMemento) -> "SolicitudDeReposicion":
        """Reconstruye el agregado desde la instantánea, validando de nuevo."""
        return cls(
            id_=uuid.UUID(memento.id),
            referencia=memento.referencia,
            cantidad_solicitada=CantidadSolicitada(memento.cantidad_solicitada),
            monto=memento.monto,
            nivel=NivelDeAprobacion(memento.nivel),
            estado=estado_por_nombre(memento.estado),
        )

    # -- lecturas ------------------------------------------------------------

    @property
    def referencia(self) -> str:
        return self._referencia

    @property
    def cantidad(self) -> CantidadSolicitada:
        return self._cantidad

    @property
    def monto(self) -> int:
        return self._monto

    @property
    def nivel(self) -> NivelDeAprobacion:
        return self._nivel

    @property
    def estado(self) -> str:
        return self._estado.nombre()
