# Ejecución del humo de Repuestos del Taller

## Qué levanta la plataforma de humo

`out/.platform/repuestos-del-taller/` la genera el orquestador (`forge assemble`): no se edita a mano.
Solo **Repuestos del Taller es real**; los demás contextos son simuladores.

| Pieza | Contenedor | Puerto interno | Ruta pública (gateway `:8080`) |
|---|---|---|---|
| Servicio real | `repuestos-del-taller` | `5102` | `/api/repuestos/…` → `/api/…` |
| Bus de eventos | `event-bus` | `5100` | `/bus/…` → `/…` |
| Simuladores (Plan de Mantenimiento, Intervenciones, Notificaciones) | `simulators` | `5110` | `/sim/…` → `/…` |
| PostgreSQL 16 | `postgres` | `5432` | solo red interna |
| Gateway | `gateway` (nginx) | `80` | `http://localhost:8080` |

El servicio lee tal cual las variables que fija el compose: `PORT`, `BUS_URL`, `SIMULATORS_URL`,
`CIFRADO_CLAVE` y `DATABASE_URL`. El `DATABASE_URL` llega con el dialecto de SQLAlchemy
(`postgresql+psycopg://…`); el servicio lo normaliza a `postgresql://` antes de `psycopg.connect`.

## Levantar solo este dominio

```bash
cd out/.platform/repuestos-del-taller
docker compose up --build --wait
```

El gateway queda en `http://localhost:8080` (se puede cambiar con `GATEWAY_PORT=…`). La plataforma
se puede levantar junto a otros dominios sin chocar: el proyecto (`COMPOSE_PROJECT`) y el puerto son
propios de este humo.

## Correr el humo

```bash
GATEWAY_URL=http://localhost:8080 python out/services/repuestos-del-taller/smoke/smoke.py
```

- Código `0` e informe `Smoke Repuestos del Taller: OK` más un renglón por paso.
- Código `1` y `Smoke Repuestos del Taller: FAIL: …` por `stderr` con el paso que no se cumplió.

El escenario, en este orden:

1. **Salud**: espera `GET /api/repuestos/health` → `{"status": "ok"}`.
2. **Registrar entrada** (`POST /api/repuestos/existencia`): 5 unidades de `HEL-T40-<sufijo>` con stock
   mínimo 1; verifica por `GET` que la física sea 5 y el estado `disponible`.
3. **Evento consumido `plan-de-mantenimiento.parada-programada.v1`**: lo dispara el simulador
   (`POST /sim/simulate/plan-de-mantenimiento/parada-programada`) y verifica por `GET` la reserva de 2
   unidades (`reservada 2`, `disponible 3`, estado `reservado`).
4. **Evento consumido `intervenciones.orden-de-trabajo-cerrada.v1`**: lo dispara el simulador
   (`POST /sim/simulate/intervenciones/orden-de-trabajo-cerrada`) y verifica el consumo (física 3, sin
   reservas, estado `consumido`).
5. **Evento publicado `repuestos-del-taller.faltante-detectado.v1`**: una parada que pide 5 unidades sin
   stock hace que el agregado levante `FaltanteDetectado`; el humo comprueba que el sobre llegó al
   suscriptor con `paradaId`, `referencia` y `cantidadFaltante` correctos (`GET /sim/received`; en el
   ensamblado completo se comprueba la entrega en `GET /bus/events`).
6. **Comandos de usuario**, cada uno verificado por `GET`: reservar repuesto, liberar reserva, ajustar
   existencia por conteo, confirmar consumo, solicitar reposición, aprobar solicitud, solicitar reposición
   y cancelar solicitud.
7. Cada paso espera con reintento hasta **60 s**; los `POST` de comando no se repiten si el servicio ya
   respondió (solo se reintenta la falta de respuesta), para no duplicar efectos.

Cada corrida usa referencias, paradas, órdenes y solicitudes nuevas (sufijo aleatorio), así que el humo se
puede repetir sobre la misma base sin que las cifras de stock cambien.

## Pruebas herméticas del servicio

Sin red, sin Docker y sin base de datos real:

```bash
cd out/services/repuestos-del-taller
python -m pytest
```

Cubren dominio, manejadores, consumidores idempotentes, outbox cifrado, sobre del bus, endpoints y los
repositorios SQL (con `sqlite3` haciendo de PostgreSQL).

## Repetir desde cero y bajar la plataforma

```bash
cd out/.platform/repuestos-del-taller
docker compose down -v          # borra la base y el estado del bus
docker compose up --build --wait
```

Ante un fallo del humo: `docker compose logs --tail 80 repuestos-del-taller` (y `event-bus`, `simulators`).

## Cómo lo corre la puerta automática

`python -m forge -d "Repuestos del Taller" gate S30-smoke` levanta la plataforma en un puerto derivado del
slug (`18000 + crc32(slug) % 2000`), con proyecto `forge-repuestos-del-taller`, ejecuta `smoke/smoke.py` con
`GATEWAY_URL` apuntando a ese puerto y baja todo con `docker compose down -v`. La puerta pasa solo si el
humo sale con código 0.
