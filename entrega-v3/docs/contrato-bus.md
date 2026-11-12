# Contrato del bus de eventos y de las APIs de interoperabilidad

> Contract-first: este documento manda sobre los servicios. Los **campos de cada evento son supuestos de diseño** (el modelo ArchiMate nombra los eventos pero no define su carga útil); se ajustan en `config/event-payloads.json` del orquestador.

## Sobre (envelope) — JSON
```json
{
  "eventId": "uuid (el mismo del evento de dominio; clave de idempotencia)",
  "topic": "<contexto>.<evento>.v1",
  "occurredOn": "ISO 8601 UTC",
  "correlationId": "uuid",
  "payload": {
    "…": "según el tópico"
  }
}
```

- Publicar: `POST http://event-bus:5100/publish` con el sobre.
- Recibir: cada servicio expone `POST /events/{topic}` (el bus lo llama con el mismo sobre; responde 2xx si procesó **o** si ya lo había procesado).
- Entrega **al menos una vez** con reintentos: los consumidores DEBEN ser idempotentes por `eventId`.
- El bus guarda los mensajes en RabbitMQ (colas durables, una por tópico y suscriptor): sobreviven a reinicios del bus y del suscriptor.
- Si el suscriptor no responde 2xx, el mensaje se reintenta tras una espera; agotados los intentos queda en la cola de mensajes muertos (`GET /dlq`, `POST /dlq/reprocesar`).
- `POST /publish` responde **202** cuando el broker confirmó el mensaje y **503** si no está disponible: el emisor reintenta desde su bandeja de salida.

## Tópicos

| Tópico | Publica | Suscriptores | Descripción |
|---|---|---|---|
| `plan-de-mantenimiento.parada-programada.v1` | Plan de Mantenimiento (simulado) | Intervenciones, Repuestos del Taller | El contexto Plan de Mantenimiento programó una parada de un dron en un taller. |
| `intervenciones.orden-de-trabajo-cerrada.v1` | Intervenciones (real) | Flota y Componentes, Plan de Mantenimiento, Repuestos del Taller, Indicadores | Intervenciones cerró una OT: consumos reales, horas-hombre y componentes con su hora de corte. |
| `repuestos-del-taller.faltante-detectado.v1` | Repuestos del Taller (real) | Intervenciones | Repuestos del Taller no pudo reservar un repuesto: la OT debe esperar. |

### `plan-de-mantenimiento.parada-programada.v1`
Campos del `payload`:
```json
{
  "paradaId": "string (uuid)",
  "dronId": "string (ADV-01…ADV-12)",
  "fechaProgramada": "string (ISO 8601)",
  "tareas": "[{tareaId: string, descripcion: string, repuestos: [{referencia: string, cantidad: int}]}]"
}
```
Ejemplo:
```json
{
  "paradaId": "11111111-1111-4111-8111-111111111111",
  "dronId": "ADV-03",
  "fechaProgramada": "2026-11-20T08:00:00Z",
  "tareas": [
    {
      "tareaId": "T-101",
      "descripcion": "Cambio de hélices",
      "repuestos": [
        {
          "referencia": "HEL-T40",
          "cantidad": 2
        }
      ]
    }
  ]
}
```

### `intervenciones.orden-de-trabajo-cerrada.v1`
Campos del `payload`:
```json
{
  "ordenId": "string (uuid)",
  "paradaId": "string (uuid)",
  "dronId": "string",
  "cerradaEn": "string (ISO 8601)",
  "horasHombre": "number",
  "consumos": "[{referencia: string, cantidad: int, numeroSerie: string|null, serieRetirada: string|null, horaDeCorte: number|null}]"
}
```
Ejemplo:
```json
{
  "ordenId": "22222222-2222-4222-8222-222222222222",
  "paradaId": "11111111-1111-4111-8111-111111111111",
  "dronId": "ADV-03",
  "cerradaEn": "2026-11-20T15:30:00Z",
  "horasHombre": 3.5,
  "consumos": [
    {
      "referencia": "HEL-T40",
      "cantidad": 2,
      "numeroSerie": null,
      "serieRetirada": null,
      "horaDeCorte": null
    },
    {
      "referencia": "BAT-22K",
      "cantidad": 1,
      "numeroSerie": "BAT-0412",
      "serieRetirada": "BAT-0377",
      "horaDeCorte": 112.5
    }
  ]
}
```

### `repuestos-del-taller.faltante-detectado.v1`
Campos del `payload`:
```json
{
  "paradaId": "string (uuid)",
  "referencia": "string",
  "cantidadFaltante": "int"
}
```
Ejemplo:
```json
{
  "paradaId": "11111111-1111-4111-8111-111111111111",
  "referencia": "HEL-T40",
  "cantidadFaltante": 1
}
```

## APIs síncronas hacia contextos simulados (capa anticorrupción)

| Servicio | Contexto proveedor | Ruta (simulador) | Mecanismo del modelo |
|---|---|---|---|
| Intervenciones | Habilitación de Personal | `/api/habilitacion-de-personal/consulta-de-habilitacion` (GET o POST) | API de consulta de habilitación |
| Repuestos del Taller | Notificaciones | `/api/notificaciones/enviar-aviso` (GET o POST) | API «Enviar aviso» |

El gateway (`http://localhost:8080`) expone: `/api/<servicio>/…` → servicios reales, `/sim/…` → simuladores. Dentro de la red de Docker los servicios llaman al simulador en `http://simulators:5110`.
