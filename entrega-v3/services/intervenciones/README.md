# Intervenciones

Microservicio del contexto **Intervenciones** (C# · Clean + DDD · MongoDB · puerto 5101): gestiona la orden de trabajo
de un dron desde que se abre una parada hasta que se libera y se cierra.

## Estructura

```
src/BuildingBlocks/        shared kernel genérico (sin conceptos de negocio), un proyecto por capa
  BuildingBlocks.Domain          Guard, Entity, AggregateRoot, DomainEvent, IBusinessRule, Especificacion, IOriginador
  BuildingBlocks.Application     CQRS, mediador, pipeline Registro → Validación → Transacción, validación, puertos
  BuildingBlocks.Infrastructure  almacén MongoDB/memoria, unidad de trabajo, BandejaDeSalida, bus HTTP, ProcesadorDeMensajeEntrante
  BuildingBlocks.Api             ProblemDetails (RFC 9457), correlación, módulos de endpoints, POST /events/{topic}
src/Intervenciones.Domain          OrdenDeTrabajo (raíz), State, Specification, Memento, eventos y reglas
src/Intervenciones.Application     comandos, consultas, validadores, consumidores, traductor de eventos, puertos
src/Intervenciones.Contracts       contratos de integración V1 y tópicos
src/Intervenciones.Infrastructure  RepositorioOrdenDeTrabajo, RepositorioCacheadoOrdenDeTrabajo, CifradorAes,
                                   PublicadorDeEventosHttp, ConsultaDeHabilitacionAdapter
src/Intervenciones.Api             IntervencionesEndpoints, solicitudes HTTP, IntervencionesComposicion, Program
tests/BuildingBlocks.Tests  tests/Intervenciones.Tests
```

Dependencias: Domain → BuildingBlocks.Domain · Contracts → nada · Application → Domain, Contracts ·
Infrastructure → Application, Domain, Contracts · Api → todas. `ReglaDeDependenciasTests` las verifica.

## Variables de entorno

| Variable | Uso |
|---|---|
| `PORT` | Puerto HTTP (5101 en el compose). |
| `MONGO_URL` | Replica set de un nodo; la orden y la bandeja de salida se guardan en una transacción. Sin ella, almacén en memoria. |
| `BUS_URL` | Bus de eventos: se publica con `POST {BUS_URL}/publish`. Sin ella, bus en memoria. |
| `SIMULATORS_URL` | Base de la API de Habilitación de Personal (obligatoria). |
| `CIFRADO_CLAVE` | Clave AES en base64 (al menos 16 bytes; obligatoria; las de 16, 24 o 32 se usan tal cual y las demás se derivan con SHA-256). Ej.: `openssl rand -base64 32`. |

## API

| Método y ruta | Comando / consulta | Respuesta |
|---|---|---|
| `POST /api/orden-de-trabajo` | Abrir orden de trabajo | 201 `{ "id": … }` |
| `GET /api/orden-de-trabajo/{id}` | Obtener orden de trabajo | 200 con la orden |
| `GET /api/orden-de-trabajo/por-parada/{paradaId}` | Obtener orden de trabajo por parada | 200 con la orden; 404 si la parada no tiene orden |
| `POST /api/orden-de-trabajo/{id}/asignar-tecnico` | Asignar técnico | 204 |
| `POST /api/orden-de-trabajo/{id}/registrar-ejecucion-de-tarea` | Registrar ejecución de tarea | 204 |
| `POST /api/orden-de-trabajo/{id}/registrar-consumo-de-repuesto` | Registrar consumo de repuesto | 204 |
| `POST /api/orden-de-trabajo/{id}/registrar-hallazgo` | Registrar hallazgo | 204 |
| `POST /api/orden-de-trabajo/{id}/registrar-vuelo-de-prueba` | Registrar vuelo de prueba | 204 |
| `POST /api/orden-de-trabajo/{id}/liberar-dron` | Liberar dron | 204 |
| `POST /api/orden-de-trabajo/{id}/cerrar-orden-de-trabajo` | Cerrar orden de trabajo (sin cuerpo) | 204 |
| `POST /api/orden-de-trabajo/{id}/poner-orden-en-espera` | Poner orden en espera | 204 |
| `POST /events/{topic}` | Entrega del bus (idempotente por `eventId`) | 200 `procesado` o `duplicado` |
| `GET /health` | Salud | 200 |

Cada comando recibe un cuerpo JSON (`…Solicitud`). Los errores salen como `application/problem+json`:
regla de negocio rota **422**, cuerpo inválido **400**, orden o tópico inexistente **404**, conflicto de versión **409**.

## Decisiones

- **Memento**: el agregado se guarda como documento `{_id, version, datos}` mediante `OrdenDeTrabajoMemento`.
- **Outbox**: el agregado y los mensajes por publicar se confirman en una sola transacción; `BandejaDeSalida` los despacha con reintentos.
- **Caché**: `RepositorioCacheadoOrdenDeTrabajo` decora la lectura de la consulta (TTL 60 s) y se invalida al confirmar cualquier cambio.
- **Cifrado**: `CifradorAes` (AES-GCM) cifra en reposo el técnico, quien ejecuta cada tarea y quien libera.
- **ACL**: `ConsultaDeHabilitacionAdapter` consulta Habilitación de Personal (timeout 5 s) y entrega al dominio solo un sí/no.
- Supuestos y decisiones menores: `docs/intervenciones/supuestos.md` y `docs/intervenciones/decisiones-arquitectura.md`.

## Ejecutar

```
dotnet build
dotnet test
docker build -t intervenciones .
docker run -p 5101:5101 -e MONGO_URL=… -e BUS_URL=… -e SIMULATORS_URL=… -e CIFRADO_CLAVE=… intervenciones
```
