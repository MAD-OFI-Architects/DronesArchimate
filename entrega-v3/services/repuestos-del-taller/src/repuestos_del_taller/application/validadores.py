"""Validación de forma, antes de construir tipos del dominio."""
from __future__ import annotations

from dataclasses import fields
from typing import Any


class _Validador:
    comando: type

    def validar(self, comando: Any) -> None:
        errores: list[str] = []
        for campo in fields(comando):
            valor = getattr(comando, campo.name)
            if isinstance(valor, str) and not valor.strip():
                errores.append(f"{campo.name} es obligatorio")
            if campo.name in {"cantidad", "stock_minimo", "plazo_dias", "conteo", "monto"}:
                if not isinstance(valor, int) or isinstance(valor, bool):
                    errores.append(f"{campo.name} debe ser entero")
        if hasattr(comando, "cantidad") and isinstance(comando.cantidad, int) and comando.cantidad <= 0:
            errores.append("cantidad debe ser positiva")
        if hasattr(comando, "conteo") and isinstance(comando.conteo, int) and comando.conteo < 0:
            errores.append("conteo no puede ser negativo")
        if hasattr(comando, "stock_minimo") and isinstance(comando.stock_minimo, int) and comando.stock_minimo < 0:
            errores.append("stock_minimo no puede ser negativo")
        if hasattr(comando, "plazo_dias") and isinstance(comando.plazo_dias, int) and comando.plazo_dias < 0:
            errores.append("plazo_dias no puede ser negativo")
        if hasattr(comando, "monto") and isinstance(comando.monto, int) and comando.monto < 0:
            errores.append("monto no puede ser negativo")
        if errores:
            raise ValueError("; ".join(errores))


from .comandos import (
    AjustarExistenciaPorConteoComando, AprobarSolicitudComando,
    CancelarSolicitudComando, ConfirmarConsumoComando, LiberarReservaComando,
    RegistrarEntradaDeRepuestoComando, ReservarRepuestoComando,
    SolicitarReposicionComando,
)

class RegistrarEntradaDeRepuestoValidador(_Validador): comando = RegistrarEntradaDeRepuestoComando
class ReservarRepuestoValidador(_Validador): comando = ReservarRepuestoComando
class LiberarReservaValidador(_Validador): comando = LiberarReservaComando
class ConfirmarConsumoValidador(_Validador): comando = ConfirmarConsumoComando
class AjustarExistenciaPorConteoValidador(_Validador): comando = AjustarExistenciaPorConteoComando
class SolicitarReposicionValidador(_Validador): comando = SolicitarReposicionComando
class AprobarSolicitudValidador(_Validador): comando = AprobarSolicitudComando
class CancelarSolicitudValidador(_Validador): comando = CancelarSolicitudComando
