"""Contratos de los eventos entre contextos (contract-first).

El modelo ArchiMate nombra los eventos pero NO define sus campos. Para que los dos servicios (C# y Python) y
los simuladores interoperen, aquí se fijan cargas útiles mínimas. Son SUPUESTOS DE DISEÑO documentados:
se pueden ajustar en `config/event-payloads.json` (se fusionan sobre estos valores) y el pipeline regenera todo.
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULTS: dict[str, dict] = {
    "Parada programada": {
        "descripcion": "El contexto Plan de Mantenimiento programó una parada de un dron en un taller.",
        "payload": {"paradaId": "string (uuid)", "dronId": "string (ADV-01…ADV-12)", "fechaProgramada": "string (ISO 8601)",
                    "tareas": "[{tareaId: string, descripcion: string, repuestos: [{referencia: string, cantidad: int}]}]"},
        "sample": {"paradaId": "11111111-1111-4111-8111-111111111111", "dronId": "ADV-03",
                   "fechaProgramada": "2026-11-20T08:00:00Z",
                   "tareas": [{"tareaId": "T-101", "descripcion": "Cambio de hélices", "repuestos": [{"referencia": "HEL-T40", "cantidad": 2}]}]},
    },
    "Orden de trabajo cerrada": {
        "descripcion": "Intervenciones cerró una OT: consumos reales, horas-hombre y componentes con su hora de corte.",
        "payload": {"ordenId": "string (uuid)", "paradaId": "string (uuid)", "dronId": "string", "cerradaEn": "string (ISO 8601)",
                    "horasHombre": "number", "consumos": "[{referencia: string, cantidad: int, numeroSerie: string|null}]"},
        "sample": {"ordenId": "22222222-2222-4222-8222-222222222222", "paradaId": "11111111-1111-4111-8111-111111111111",
                   "dronId": "ADV-03", "cerradaEn": "2026-11-20T15:30:00Z", "horasHombre": 3.5,
                   "consumos": [{"referencia": "HEL-T40", "cantidad": 2, "numeroSerie": None}]},
    },
    "Faltante detectado": {
        "descripcion": "Repuestos del Taller no pudo reservar un repuesto: la OT debe esperar.",
        "payload": {"paradaId": "string (uuid)", "referencia": "string", "cantidadFaltante": "int"},
        "sample": {"paradaId": "11111111-1111-4111-8111-111111111111", "referencia": "HEL-T40", "cantidadFaltante": 1},
    },
    "Enviar aviso": {
        "descripcion": "Aviso por correo/WhatsApp (API síncrona del contexto Notificaciones; no viaja por el bus).",
        "payload": {"canal": "string (correo|whatsapp)", "destinatario": "string", "asunto": "string", "mensaje": "string"},
        "sample": {"canal": "correo", "destinatario": "almacen@agrodrones.example", "asunto": "Stock mínimo", "mensaje": "HEL-T40 llegó al mínimo"},
    },
}
GENERIC = {"descripcion": "Evento de dominio entre contextos.", "payload": {"aggregateId": "string", "ocurridoEn": "string (ISO 8601)"},
           "sample": {"aggregateId": "00000000-0000-4000-8000-000000000000", "ocurridoEn": "2026-11-20T00:00:00Z"}}


def load(root: Path) -> dict[str, dict]:
    out = {k: dict(v) for k, v in DEFAULTS.items()}
    p = root / "config" / "event-payloads.json"
    if p.exists():
        out.update(json.loads(p.read_text(encoding="utf-8")))
    return out


def for_event(table: dict[str, dict], name: str) -> dict:
    return table.get(name, GENERIC)
