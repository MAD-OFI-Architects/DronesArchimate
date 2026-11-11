"""Puertos para efectos externos al caso de uso."""
from __future__ import annotations

from abc import ABC, abstractmethod


class IEnviarAviso(ABC):
    @abstractmethod
    def enviar(self, destinatario: str, asunto: str, mensaje: str) -> None:
        """Envía un aviso mediante el proveedor externo traducido por ACL."""


class Cifrador(ABC):
    @abstractmethod
    def cifrar(self, texto: str) -> str: ...

    @abstractmethod
    def descifrar(self, texto: str) -> str: ...


class IPublicadorDeEventos(ABC):
    """Salida de eventos de integración: la implementación los escribe en la bandeja de salida (outbox)."""

    @abstractmethod
    def publicar(self, topico: str, payload: dict) -> None: ...
