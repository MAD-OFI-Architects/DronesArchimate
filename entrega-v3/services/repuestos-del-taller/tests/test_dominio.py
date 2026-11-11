from __future__ import annotations

import uuid

import pytest

from repuestos_del_taller.domain.compartido.errores import (
    ErrorDeDominio,
    ViolacionDeReglaDeNegocio,
)
from repuestos_del_taller.domain.existencias.eventos import (
    ConsumoConfirmado,
    ExistenciaAjustada,
    FaltanteDetectado,
    RepuestoRecibido,
    RepuestoReservado,
    ReservaLiberada,
    StockMinimoAlcanzado,
)
from repuestos_del_taller.domain.existencias.existencia import Existencia
from repuestos_del_taller.domain.existencias.objetos_de_valor import (
    Cantidad,
    PlazoDeEntrega,
    StockMinimo,
)
from repuestos_del_taller.domain.reposicion.eventos import (
    ReposicionSolicitada,
    SolicitudAprobada,
    SolicitudCancelada,
)
from repuestos_del_taller.domain.reposicion.objetos_de_valor import (
    CantidadSolicitada,
    NivelDeAprobacion,
)
from repuestos_del_taller.domain.reposicion.solicitud_de_reposicion import (
    SolicitudDeReposicion,
)


def existencia(cantidad: int = 10, minimo: int = 2) -> Existencia:
    return Existencia.registrar_entrada(
        "FILTRO-T40", Cantidad(cantidad), StockMinimo(minimo), PlazoDeEntrega(3)
    )


def tipos_eventos(agregado: object) -> list[type]:
    return [type(evento) for evento in agregado.eventos]


def test_registrar_entrada_emite_repuesto_recibido() -> None:
    agregado = existencia(6)

    assert tipos_eventos(agregado) == [RepuestoRecibido]
    assert agregado.fisica == Cantidad(6)
    assert agregado.disponible == 6


def test_registrar_entrada_rechaza_cantidad_no_positiva() -> None:
    with pytest.raises(ErrorDeDominio):
        existencia(0)


def test_reservar_repuesto_emite_repuesto_reservado() -> None:
    agregado = existencia()

    reserva = agregado.reservar("OT-1", Cantidad(4))

    assert reserva.orden_trabajo_id == "OT-1"
    assert tipos_eventos(agregado)[-1] is RepuestoReservado
    assert agregado.reservada == 4
    assert agregado.disponible == 6


def test_reservar_repuesto_rechaza_existencia_insuficiente_y_emite_faltante() -> None:
    agregado = existencia(3)

    with pytest.raises(ViolacionDeReglaDeNegocio) as error:
        agregado.reservar("OT-1", Cantidad(4))

    assert type(error.value.regla).__name__ == "ExistenciaInsuficiente"
    assert isinstance(agregado.eventos[-1], FaltanteDetectado)
    assert agregado.disponible == 3


def test_liberar_reserva_emite_reserva_liberada() -> None:
    agregado = existencia()
    agregado.reservar("OT-1", Cantidad(4))
    agregado.liberar_reserva("OT-1")

    assert tipos_eventos(agregado)[-1] is ReservaLiberada
    assert agregado.reservada == 0
    assert agregado.estado == "disponible"


def test_liberar_reserva_inexistente_rompe_la_regla_operativa() -> None:
    with pytest.raises(ErrorDeDominio):
        existencia().liberar_reserva("OT-404")


def test_confirmar_consumo_emite_consumo_y_stock_minimo() -> None:
    agregado = existencia(5, minimo=2)
    agregado.reservar("OT-1", Cantidad(3))

    agregado.confirmar_consumo("OT-1")

    assert isinstance(agregado.eventos[-2], ConsumoConfirmado)
    assert isinstance(agregado.eventos[-1], StockMinimoAlcanzado)
    assert agregado.disponible == 2
    assert agregado.estado == "bajo_minimo"


def test_confirmar_consumo_sin_reserva_rompe_la_regla_operativa() -> None:
    with pytest.raises(ErrorDeDominio):
        existencia().confirmar_consumo("OT-404")


def test_ajustar_existencia_por_conteo_emite_existencia_ajustada() -> None:
    agregado = existencia()

    agregado.ajustar_existencia_por_conteo(Cantidad(7))

    assert isinstance(agregado.eventos[-1], ExistenciaAjustada)
    assert agregado.fisica == Cantidad(7)


def test_ajustar_existencia_por_conteo_no_baja_de_lo_reservado() -> None:
    agregado = existencia()
    agregado.reservar("OT-1", Cantidad(4))

    with pytest.raises(ViolacionDeReglaDeNegocio) as error:
        agregado.ajustar_existencia_por_conteo(Cantidad(3))

    assert type(error.value.regla).__name__ == "ExistenciaInsuficiente"
    assert agregado.fisica == Cantidad(10)


def test_solicitar_reposicion_emite_reposicion_solicitada() -> None:
    solicitud = SolicitudDeReposicion.solicitar(
        uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 5_000_000, False
    )

    assert isinstance(solicitud.eventos[-1], ReposicionSolicitada)
    assert solicitud.estado == "abierta"
    assert solicitud.nivel == NivelDeAprobacion(NivelDeAprobacion.JEFE)


def test_solicitar_reposicion_rechaza_otra_solicitud_abierta() -> None:
    with pytest.raises(ViolacionDeReglaDeNegocio) as error:
        SolicitudDeReposicion.solicitar(
            uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 100, True
        )

    assert type(error.value.regla).__name__ == "SolicitudAbierta"


def test_aprobar_solicitud_emite_solicitud_aprobada() -> None:
    solicitud = SolicitudDeReposicion.solicitar(
        uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 5_000_001, False
    )

    solicitud.aprobar()

    assert isinstance(solicitud.eventos[-1], SolicitudAprobada)
    assert solicitud.nivel.requiere_gerencia
    assert solicitud.estado == "aprobada"


def test_aprobar_solicitud_cancelada_es_una_transicion_invalida() -> None:
    solicitud = SolicitudDeReposicion.solicitar(
        uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 100, False
    )
    solicitud.cancelar()

    with pytest.raises(ErrorDeDominio):
        solicitud.aprobar()


def test_cancelar_solicitud_emite_solicitud_cancelada() -> None:
    solicitud = SolicitudDeReposicion.solicitar(
        uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 100, False
    )

    solicitud.cancelar()

    assert isinstance(solicitud.eventos[-1], SolicitudCancelada)
    assert solicitud.estado == "cancelada"


def test_cancelar_solicitud_aprobada_es_una_transicion_invalida() -> None:
    solicitud = SolicitudDeReposicion.solicitar(
        uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 100, False
    )
    solicitud.aprobar()

    with pytest.raises(ErrorDeDominio):
        solicitud.cancelar()


def test_memento_de_existencia_restaura_el_estado_completo() -> None:
    original = existencia(10, 2)
    original.reservar("OT-1", Cantidad(4))
    memento = original.crear_memento()

    restaurada = Existencia.restaurar_desde(memento)

    assert restaurada.crear_memento() == memento
    assert restaurada.disponible == 6


def test_memento_de_solicitud_restaura_el_estado_completo() -> None:
    original = SolicitudDeReposicion.solicitar(
        uuid.uuid4(), "FILTRO-T40", CantidadSolicitada(2), 5_000_001, False
    )
    original.aprobar()
    memento = original.crear_memento()

    restaurada = SolicitudDeReposicion.restaurar_desde(memento)

    assert restaurada.crear_memento() == memento
    assert restaurada.estado == "aprobada"


def test_consumos_sucesivos_desde_bajo_minimo_no_corrompen_el_agregado() -> None:
    e = existencia(10, 5)
    e.reservar("A", Cantidad(3))
    e.reservar("B", Cantidad(3))
    e.confirmar_consumo("A")
    assert e.estado == "bajo_minimo"
    e.confirmar_consumo("B")
    assert (e.fisica.valor, e.reservada) == (4, 0)
