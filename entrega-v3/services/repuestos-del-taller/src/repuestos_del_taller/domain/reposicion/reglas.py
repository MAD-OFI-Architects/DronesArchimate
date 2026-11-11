"""Regla de negocio del agregado «Solicitud de reposición» (código del contrato)."""
from __future__ import annotations


class SolicitudAbierta:
    """SOLICITUD_ABIERTA: ya existe una solicitud abierta para la referencia;
    el contrato impone una solicitud abierta por referencia."""

    def __init__(self, hay_abierta: bool, referencia: str = "") -> None:
        self._hay_abierta = hay_abierta
        self._referencia = referencia

    def es_rota(self) -> bool:
        return self._hay_abierta

    @property
    def mensaje(self) -> str:
        return (
            f"Ya existe una solicitud abierta para la referencia "
            f"'{self._referencia}'."
        )
