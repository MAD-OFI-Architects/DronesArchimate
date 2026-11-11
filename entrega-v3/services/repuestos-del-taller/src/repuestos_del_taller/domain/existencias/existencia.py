"""Raíz del agregado «Existencia»: unidades que el taller puede usar hoy,
sin contar lo reservado. Un método de negocio por comando del modelo; cada
comando valida sus reglas y levanta su evento de dominio.
"""
from __future__ import annotations

import uuid
from typing import Sequence

from ..compartido.agregados import RaizDeAgregado
from ..compartido.errores import ErrorDeDominio, ViolacionDeReglaDeNegocio
from ..compartido.guard import Guard
from ..compartido.reglas import verificar_regla
from .estados import (
    BajoMinimo,
    Consumido,
    Disponible,
    EstadoExistencia,
    Reponiendo,
    Reservado,
    estado_por_nombre,
)
from .eventos import (
    ConsumoConfirmado,
    ExistenciaAjustada,
    FaltanteDetectado,
    RepuestoRecibido,
    RepuestoReservado,
    ReservaLiberada,
    StockMinimoAlcanzado,
)
from .memento import ExistenciaMemento, ReservaDeRepuestoMemento
from .objetos_de_valor import Cantidad, PlazoDeEntrega, StockMinimo
from .reglas import ExistenciaInsuficiente
from .reserva_de_repuesto import ReservaDeRepuesto


class Existencia(RaizDeAgregado[str]):
    """Existencia de una referencia de repuesto en el taller.

    La identidad de la raíz es la referencia del repuesto; ``reservado <=
    física`` es la invariante que sostiene (existencia usable = física −
    reservada).
    """

    def __init__(
        self,
        referencia: str,
        fisica: Cantidad,
        stock_minimo: StockMinimo,
        plazo: PlazoDeEntrega,
        estado: EstadoExistencia | None = None,
        reservas: Sequence[ReservaDeRepuesto] = (),
    ) -> None:
        super().__init__(Guard.texto(referencia, "referencia"))
        Guard.no_nulo(fisica, "física")
        Guard.no_nulo(stock_minimo, "stock mínimo")
        Guard.no_nulo(plazo, "plazo de entrega")
        Guard.no_nulo(reservas, "reservas")
        self._fisica = fisica
        self._stock_minimo = stock_minimo
        self._plazo = plazo
        self._estado = estado if estado is not None else Disponible()
        self._reservas: list[ReservaDeRepuesto] = list(reservas)
        self._verificar_invariantes()

    # -- comandos del modelo -------------------------------------------------

    @classmethod
    def registrar_entrada(
        cls,
        referencia: str,
        cantidad: Cantidad,
        stock_minimo: StockMinimo,
        plazo: PlazoDeEntrega,
    ) -> "Existencia":
        """Registrar entrada de repuesto → RepuestoRecibido (primera entrada)."""
        Guard.texto(referencia, "referencia")
        Guard.positivo(cantidad.valor, "cantidad de la entrada")
        entrada = cls(referencia, cantidad, stock_minimo, plazo, Disponible(), ())
        entrada.levantar(
            RepuestoRecibido(
                referencia=entrada.referencia,
                cantidad=cantidad.valor,
                fisica=entrada.fisica.valor,
                plazo_dias=plazo.dias,
            )
        )
        return entrada

    def recibir(self, cantidad: Cantidad) -> None:
        """Entrada posterior de la misma referencia → RepuestoRecibido."""
        Guard.positivo(cantidad.valor, "cantidad de la entrada")
        self._fisica = self._fisica.sumar(cantidad)
        if not self._reservas:
            self._estado = self._estado.transitar_a(Disponible())
        self.levantar(
            RepuestoRecibido(
                referencia=self.referencia,
                cantidad=cantidad.valor,
                fisica=self._fisica.valor,
                plazo_dias=self._plazo.dias,
            )
        )

    def reservar(self, orden_trabajo_id: str, cantidad: Cantidad) -> ReservaDeRepuesto:
        """Reservar repuesto → RepuestoReservado; si no alcanza la existencia
        usable levanta FaltanteDetectado y la regla ExistenciaInsuficiente."""
        ot = Guard.texto(orden_trabajo_id, "orden de trabajo")
        Guard.positivo(cantidad.valor, "cantidad a reservar")
        existente = self._reserva_de(ot)
        if existente is not None:
            if existente.cantidad == cantidad:
                return existente
            raise ErrorDeDominio(
                f"La orden de trabajo '{ot}' ya tiene una reserva de "
                f"{existente.cantidad.valor} unidades."
            )
        regla = ExistenciaInsuficiente(cantidad.valor, self.disponible)
        if regla.es_rota():
            self.levantar(
                FaltanteDetectado(
                    referencia=self.referencia,
                    orden_trabajo_id=ot,
                    solicitada=cantidad.valor,
                    disponible=self.disponible,
                )
            )
            raise ViolacionDeReglaDeNegocio(regla)
        reserva = ReservaDeRepuesto(uuid.uuid4(), ot, cantidad)
        self._reservas.append(reserva)
        self._estado = self._estado.transitar_a(Reservado())
        self.levantar(
            RepuestoReservado(
                referencia=self.referencia,
                orden_trabajo_id=ot,
                cantidad=cantidad.valor,
                reservada=self.reservada,
            )
        )
        return reserva

    def liberar_reserva(self, orden_trabajo_id: str) -> None:
        """Liberar reserva → ReservaLiberada; sin reservas vuelve a disponible."""
        ot = Guard.texto(orden_trabajo_id, "orden de trabajo")
        reserva = self._reserva_de(ot)
        if reserva is None:
            raise ErrorDeDominio(
                f"No hay reserva de la orden de trabajo '{ot}' para "
                f"'{self.referencia}'."
            )
        self._reservas.remove(reserva)
        self.levantar(
            ReservaLiberada(
                referencia=self.referencia,
                orden_trabajo_id=ot,
                cantidad=reserva.cantidad.valor,
            )
        )
        if not self._reservas:
            self._estado = self._estado.transitar_a(Disponible())

    def confirmar_consumo(self, orden_trabajo_id: str) -> None:
        """Confirmar consumo → ConsumoConfirmado; si la existencia usable queda
        en el stock mínimo o por debajo, además levanta StockMinimoAlcanzado y
        pasa a bajo mínimo."""
        ot = Guard.texto(orden_trabajo_id, "orden de trabajo")
        reserva = self._reserva_de(ot)
        if reserva is None:
            raise ErrorDeDominio(
                f"No hay reserva de la orden de trabajo '{ot}' para "
                f"'{self.referencia}'."
            )
        cantidad = reserva.cantidad
        self._fisica = Cantidad(self._fisica.valor - cantidad.valor)
        self._reservas.remove(reserva)
        self.levantar(
            ConsumoConfirmado(
                referencia=self.referencia,
                orden_trabajo_id=ot,
                cantidad=cantidad.valor,
            )
        )
        self._estado = self._estado.transitar_a(Consumido())
        if self.disponible <= self._stock_minimo.valor:
            self._estado = self._estado.transitar_a(BajoMinimo())
            self.levantar(
                StockMinimoAlcanzado(
                    referencia=self.referencia,
                    disponible=self.disponible,
                    stock_minimo=self._stock_minimo.valor,
                )
            )

    def ajustar_existencia_por_conteo(self, conteo: Cantidad) -> None:
        """Ajustar existencia por conteo → ExistenciaAjustada; el ajuste no
        puede dejar la física por debajo de lo ya reservado."""
        Guard.no_nulo(conteo, "conteo")
        verificar_regla(ExistenciaInsuficiente(self.reservada, conteo.valor))
        anterior = self._fisica.valor
        self._fisica = conteo
        self.levantar(
            ExistenciaAjustada(
                referencia=self.referencia,
                fisica_anterior=anterior,
                fisica_nueva=conteo.valor,
            )
        )

    def iniciar_reposicion(self) -> None:
        """Marca la existencia como reponiendo cuando la solicitud de reposición
        fue aprobada (el modelo no levanta evento por esta transición)."""
        self._estado = self._estado.transitar_a(Reponiendo())

    # -- memento -------------------------------------------------------------

    def crear_memento(self) -> ExistenciaMemento:
        return ExistenciaMemento(
            referencia=self.referencia,
            fisica=self._fisica.valor,
            stock_minimo=self._stock_minimo.valor,
            plazo_dias=self._plazo.dias,
            estado=self._estado.nombre(),
            reservas=tuple(
                ReservaDeRepuestoMemento(
                    id=str(reserva.id),
                    orden_trabajo_id=reserva.orden_trabajo_id,
                    cantidad=reserva.cantidad.valor,
                )
                for reserva in self._reservas
            ),
        )

    @classmethod
    def restaurar_desde(cls, memento: ExistenciaMemento) -> "Existencia":
        """Reconstruye el agregado desde la instantánea, validando de nuevo."""
        return cls(
            referencia=memento.referencia,
            fisica=Cantidad(memento.fisica),
            stock_minimo=StockMinimo(memento.stock_minimo),
            plazo=PlazoDeEntrega(memento.plazo_dias),
            estado=estado_por_nombre(memento.estado),
            reservas=tuple(
                ReservaDeRepuesto(
                    uuid.UUID(reserva.id),
                    reserva.orden_trabajo_id,
                    Cantidad(reserva.cantidad),
                )
                for reserva in memento.reservas
            ),
        )

    # -- lecturas ------------------------------------------------------------

    @property
    def referencia(self) -> str:
        return self.id

    @property
    def fisica(self) -> Cantidad:
        return self._fisica

    @property
    def stock_minimo(self) -> StockMinimo:
        return self._stock_minimo

    @property
    def plazo(self) -> PlazoDeEntrega:
        return self._plazo

    @property
    def reservada(self) -> int:
        return sum(reserva.cantidad.valor for reserva in self._reservas)

    @property
    def disponible(self) -> int:
        return self._fisica.valor - self.reservada

    @property
    def estado(self) -> str:
        return self._estado.nombre()

    # -- internos ------------------------------------------------------------

    def _reserva_de(self, orden_trabajo_id: str) -> ReservaDeRepuesto | None:
        return next(
            (reserva for reserva in self._reservas
             if reserva.orden_trabajo_id == orden_trabajo_id),
            None,
        )

    def _verificar_invariantes(self) -> None:
        if self.reservada > self._fisica.valor:
            raise ErrorDeDominio(
                f"La cantidad reservada ({self.reservada}) no puede superar la "
                f"física ({self._fisica.valor})."
            )
