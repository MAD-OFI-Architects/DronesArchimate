"""Cifrado de datos personales en reposo."""
from __future__ import annotations

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ...application.puertos import Cifrador


class CifradorAes(Cifrador):
    """AES-GCM con nonce aleatorio; la clave llega por ``CIFRADO_CLAVE``."""

    def __init__(self, clave: str | bytes | None = None) -> None:
        raw = clave or os.getenv("CIFRADO_CLAVE", "")
        self._clave = self._decodificar(raw)
        if len(self._clave) not in (16, 24, 32):
            self._clave = hashlib.sha256(self._clave or b"clave-local").digest()

    @staticmethod
    def _decodificar(raw: str | bytes) -> bytes:
        if isinstance(raw, bytes):
            return raw
        try:
            return base64.b64decode(raw, validate=True)
        except ValueError:
            return raw.encode()

    def cifrar(self, texto: str) -> str:
        nonce = os.urandom(12)
        return base64.urlsafe_b64encode(nonce + AESGCM(self._clave).encrypt(nonce, texto.encode(), None)).decode()

    def descifrar(self, texto: str) -> str:
        raw = base64.urlsafe_b64decode(texto.encode())
        return AESGCM(self._clave).decrypt(raw[:12], raw[12:], None).decode()
