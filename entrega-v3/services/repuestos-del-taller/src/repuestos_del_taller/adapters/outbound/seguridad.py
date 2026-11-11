"""Cifrado de datos personales en reposo."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os

from ...application.puertos import Cifrador


class CifradorAes(Cifrador):
    """AES-GCM cuando ``cryptography`` está disponible, con nonce autenticado."""

    def __init__(self, clave: str | bytes | None = None) -> None:
        raw = clave or os.getenv("CIFRADO_CLAVE", "")
        self._clave = base64.b64decode(raw) if isinstance(raw, str) else raw
        if len(self._clave) not in (16, 24, 32):
            self._clave = hashlib.sha256(self._clave or b"clave-local").digest()

    def cifrar(self, texto: str) -> str:
        nonce = os.urandom(12)
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            valor = AESGCM(self._clave).encrypt(nonce, texto.encode(), None)
        except ImportError:
            valor = self._fallback(nonce, texto.encode())
        return base64.urlsafe_b64encode(nonce + valor).decode()

    def descifrar(self, texto: str) -> str:
        raw = base64.urlsafe_b64decode(texto.encode())
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            return AESGCM(self._clave).decrypt(raw[:12], raw[12:], None).decode()
        except ImportError:
            return self._unfallback(raw[:12], raw[12:]).decode()

    def _fallback(self, nonce: bytes, claro: bytes) -> bytes:
        """Fallback para el entorno mínimo; en imagen de producción se usa AES-GCM."""
        flujo = hashlib.sha256(self._clave + nonce).digest()
        cifrado = bytes(byte ^ flujo[i % len(flujo)] for i, byte in enumerate(claro))
        return cifrado + hmac.new(self._clave, nonce + cifrado, hashlib.sha256).digest()

    def _unfallback(self, nonce: bytes, valor: bytes) -> bytes:
        cifrado, tag = valor[:-32], valor[-32:]
        if not hmac.compare_digest(tag, hmac.new(self._clave, nonce + cifrado, hashlib.sha256).digest()):
            raise ValueError("cifrado alterado")
        flujo = hashlib.sha256(self._clave + nonce).digest()
        return bytes(byte ^ flujo[i % len(flujo)] for i, byte in enumerate(cifrado))
