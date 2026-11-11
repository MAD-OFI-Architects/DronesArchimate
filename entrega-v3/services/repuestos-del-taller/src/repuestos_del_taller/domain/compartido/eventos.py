"""Eventos de dominio: registros inmutables de algo que ya pasó, con su propio
identificador y fecha. El ``evento_id`` viaja hasta el mensaje de integración y
sirve como clave de idempotencia en los consumidores.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, kw_only=True)
class EventoDeDominio:
    """Base de los eventos de dominio (inmutable)."""

    evento_id: uuid.UUID = field(default_factory=uuid.uuid4)
    ocurrio_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
