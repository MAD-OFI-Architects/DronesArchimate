# Entrega V3 — producto generado desde el modelo ArchiMate

Este directorio es la **salida ejecutable** de ArchiForge. Está generado a partir de:

- `diseno/modelo/drones-mantenimiento.archimate`
- las decisiones de arquitectura de `archiforge/decisiones/`

No hace falta volver a ejecutar el generador para levantar el producto: todo lo necesario está incluido.

## Dominios implementados

| Dominio | Lenguaje | Arquitectura | Base de datos | Patrones |
|---|---|---|---|---|
| **Intervenciones** | C# (.NET 8) | Clean Architecture + DDD | MongoDB (replica set) | 10 |
| **Repuestos del Taller** | Python (FastAPI) | Hexagonal | PostgreSQL | 7 |

Los demás contextos del modelo están **simulados**. Los servicios se comunican por **eventos** a través de un bus respaldado por **RabbitMQ** (colas durables, reintentos y cola de mensajes muertos); solo las consultas puntuales (habilitación y avisos) son llamadas directas. Explicación completa en el [manual](../docs/manual/README.md).

## Requisitos

- Docker con Compose v2
- El usuario debe tener acceso al socket de Docker (`docker ps` sin `permission denied`)
- Python 3 solo para correr los smoke tests desde el host (opcional: también pueden correrse dentro de la red)

## Levantar todo

```bash
cd entrega-v3
GATEWAY_PORT=8080 docker compose up --build --wait
```

Gateway: `http://localhost:8080` · Consola de RabbitMQ: `http://localhost:15672` (usuario y clave `guest`; cambiable con `RABBITMQ_UI_PORT`).

Son **8 contenedores**: gateway, intervenciones, repuestos-del-taller, event-bus, rabbitmq, simulators, mongo y postgres.

| Ruta | Destino |
|---|---|
| `/` | Shell de microfrontends |
| `/mfe/mfe-intervenciones/` | Web Component de Intervenciones |
| `/mfe/mfe-repuestos-del-taller/` | Web Component de Repuestos |
| `/api/intervenciones/...` | Servicio C# |
| `/api/repuestos/...` | Servicio Python |
| `/sim/simulate/<contexto>/<evento>` | Simuladores publican un evento |
| `/sim/received` | Eventos recibidos por los simuladores |
| `/sim/health` | Salud de los simuladores |
| `/bus/health` | Estado del bus (debe decir `rabbitmq`) |
| `/bus/dlq` | Mensajes que no se pudieron entregar, por cola |
| `/bus/dlq/reprocesar` (POST) | Devuelve los mensajes muertos a su cola |

Apagar:

```bash
docker compose down -v
```

## Datos de demostración

```bash
python3 seed/seed.py
```

Carga por la API 8 repuestos, 3 solicitudes de reposición y 6 órdenes de trabajo en seis estados distintos (dos de ellas nacen por evento, para ver la integración entre servicios). Es idempotente. Detalle en [`seed/README.md`](seed/README.md).

## Smoke tests

Con la plataforma levantada:

```bash
python3 services/intervenciones/smoke/smoke.py
python3 services/repuestos-del-taller/smoke/smoke.py
```

Ambos usan `GATEWAY_URL` (por defecto `http://localhost:8080`). Los eventos de contextos simulados se publican por `/sim/simulate`; los eventos de dominios reales, por el bus real (`/bus/publish`).

## Probar un dominio aislado

Cada dominio tiene su propia plataforma de humo, sin el otro dominio:

```bash
cd .platform/intervenciones && docker compose up --build --wait
# o
cd .platform/repuestos-del-taller && docker compose up --build --wait
```

Usan puertos propios para no chocar entre sí.

## Estructura

```text
entrega-v3/
├── docker-compose.yml        plataforma completa (2 dominios reales + bus + RabbitMQ + simuladores + gateway)
├── nginx.conf                proxy del gateway ensamblado
├── init-postgres.sql         base de datos PostgreSQL de Repuestos
├── services/
│   ├── intervenciones/       solución .NET (domain, application, infrastructure, api, contracts, tests, smoke)
│   └── repuestos-del-taller/ servicio Python (domain, application, adapters, tests, smoke)
├── frontend/
│   ├── Dockerfile            construye los tres microfrontends
│   ├── nginx.conf            proxy + estáticos
│   ├── mfe-shell/            host que integra los remotes
│   ├── mfe-intervenciones/   Web Component de Intervenciones
│   └── mfe-repuestos-del-taller/
├── event-bus/                puente de eventos sobre RabbitMQ (tópicos, reintentos, cola de mensajes muertos)
├── simulators/               contextos no implementados
├── seed/                     datos de demostración (idempotente)
├── .platform/                plataformas de humo aisladas por dominio
└── docs/                     ADR, trazabilidad, contrato del bus, verificación
```

## Documentación

- `docs/intervenciones/decisiones-arquitectura.md` — ADR con la justificación de lenguaje, arquitectura, BD y cada patrón
- `docs/intervenciones/verificacion.md` — revisión independiente
- `docs/intervenciones/trazabilidad.md` — símbolo del modelo → archivo
- `docs/repuestos-del-taller/` — equivalentes del segundo dominio
- `docs/contrato-bus.md` — contrato de eventos y APIs de interoperabilidad

El paso a paso completo del proceso está en [`../docs/guia-ejecucion-v3.md`](../docs/guia-ejecucion-v3.md).

## Límites conocidos

Resumen (el detalle y cómo se corregirían está en [`../docs/manual/08-calidad-y-pruebas.md`](../docs/manual/08-calidad-y-pruebas.md)):

- **Repuestos debe correr como una sola instancia**: con dos réplicas se pierden reservas (comprobado; falta control de versión en el guardado).
- El outbox de Repuestos es durable pero no comparte transacción con el agregado; el de Intervenciones sí.
- El bus no valida el contenido de los eventos contra el contrato.
- No hay autenticación en el gateway ni entre servicios; el filtro por rol es solo de interfaz.

## Nota sobre seguridad

La clave de cifrado incluida (`CIFRADO_CLAVE`) es una clave **de desarrollo** generada para la demo. En un despliegue real debe venir de un gestor de secretos.
