# Datos de demostración

Carga un taller creíble **directamente por la API** (a través del gateway), para mostrar el sistema con información real en las pantallas.

```bash
cd entrega-v3
GATEWAY_PORT=8080 docker compose up --build --wait     # si todavía no está levantado
python3 seed/seed.py                                    # contra http://localhost:8080
GATEWAY_URL=http://localhost:18080 python3 seed/seed.py # contra otro puerto
```

Solo usa la biblioteca estándar de Python 3. El script imprime al final los identificadores para pegarlos en las consultas de la interfaz.

## Qué crea

**Repuestos del Taller** (8 repuestos, 3 solicitudes)

| Referencia | Existencia | Mínimo | Particularidad |
|---|---|---|---|
| HEL-T40 | 3 | 2 | la parada de ADV-02 pide 5 → faltante |
| MOT-X8 | 6 | 2 | consumido con serie en ADV-05 |
| BAT-22K | 12 | 4 | 2 unidades reservadas para `OT-DEMO-RESERVA` (estado «reservado») |
| BOM-12 | 4 → 3 | 2 | baja a 3 al cerrarse ADV-06 (integración) |
| BOQ-FAN | 40 → 38 | 10 | ajustada por conteo físico |
| ESC-60, GPS-RTK, TRD-LIM | 5, 2, 8 | 2, 1, 3 | |

Solicitudes de reposición: una **abierta** (GPS-RTK), una **aprobada** (BOM-12) y una **cancelada** (ESC-60).

**Intervenciones** (6 órdenes, una en cada estado)

| Dron | Estado | Cómo nace | Qué muestra |
|---|---|---|---|
| ADV-01 | Abierta | por API | orden recién abierta |
| ADV-02 | En espera | por **evento** | la parada pide más hélices de las que hay: Repuestos avisa del faltante |
| ADV-03 | En ejecución | por API | técnico asignado y una tarea ejecutada |
| ADV-04 | Ejecutada | por API | tarea, consumo, hallazgo y vuelo aprobado |
| ADV-05 | Liberada | por API | **trabajo mayor**: lo libera otra persona; consumo con número de serie |
| ADV-06 | Cerrada | por **evento** | ciclo completo; al cerrar, Repuestos descuenta lo consumido |

## Idempotente y reanudable

Los identificadores son deterministas y antes de cada paso se mira el estado actual: se puede correr varias veces sin duplicar nada, y si una corrida se interrumpe a medias, la siguiente continúa donde quedó. Para empezar de cero: `docker compose down -v`.

## Pruebas

```bash
python3 -m unittest seed/test_seed.py -v    # sin Docker: API falsa con las reglas reales de los servicios
```
