# Verificación independiente — Repuestos del Taller (S50)

Revisor externo. Alcance: `out/services/repuestos-del-taller/`, `out/frontend/mfe-repuestos-del-taller/`, `out/docs/repuestos-del-taller/`.
Pruebas ejecutadas: servicio `pytest` → **26 passed** (21 previas + 5 de regresión); microfrontend `vitest run` → **8 passed**.

| Criterio | Hallazgo | Severidad | Estado (corregido/pendiente) | Evidencia |
|---|---|---|---|---|
| Decisiones: lenguaje, arquitectura, estilo | Python/FastAPI, hexagonal (`domain`/`application`/`adapters`), microservicio con puerto 5102. Coincide con lo decidido. | — | corregido (conforme) | `pyproject.toml`, `adapters/inbound/http/composicion.py` |
| Decisiones: base de datos | Los repositorios son en memoria; `DATABASE_URL` no se lee y no hay driver PostgreSQL. | Alta | pendiente (límite declarado en ADR §9) | `adapters/outbound/persistencia.py:20-33` |
| Patrón State | Bug: `confirmar_consumo` desde `bajo_minimo`/`reponiendo` lanzaba error **después** de mutar el agregado (física y reservas cambiadas, excepción igualmente). | Alta | corregido | `domain/existencias/estados.py`; prueba `test_consumos_sucesivos_desde_bajo_minimo_no_corrompen_el_agregado` |
| Patrón State | El estado `reponiendo` nunca se alcanzaba (`iniciar_reposicion` sin llamadas). | Media | corregido | `AprobarSolicitudManejador._iniciar_reposicion`; prueba `test_aprobar_la_solicitud_pone_la_existencia_en_reponiendo` |
| Política del IR «Stock mínimo alcanzado → Solicitar reposición» | `StockMinimoAlcanzadoObservador` existía pero no estaba conectado: la política nunca se ejecutaba. | Alta | corregido | `ConfirmarConsumoManejador._notificar_stock_minimo`, `composicion.py`; prueba `test_stock_minimo_alcanzado_dispara_solicitar_reposicion` |
| Eventos de integración | La ruta HTTP de reservar usaba un manejador sin publicador: el `Faltante detectado` no salía al bus. Ahora un único manejador compartido. | Media | corregido | `composicion.py`; prueba `test_reservar_por_http_publica_el_faltante` |
| Validación de entrada | Un cuerpo inválido (campos faltantes, UUID mal formado) producía 500 o 404 (`ValueError`→404). Ahora 422. | Media | corregido | `adapters/inbound/http/endpoints.py`; prueba `test_cuerpo_invalido_responde_422_y_no_500` |
| Patrón Outbox | `BandejaDeSalida` existe pero no se usa; la publicación es directa y no transaccional. | Media | pendiente (requiere BD real) | `adapters/outbound/integracion.py:41` |
| Patrón Cifrado | `CifradorAes` existe y se prueba, pero ningún caso de uso cifra datos; el fallback sin `cryptography` es XOR+HMAC propio, no AES. | Media | pendiente | `adapters/outbound/seguridad.py` |
| Patrón ACL | `IEnviarAviso`/`EnviarAvisoAdapter` existen pero ningún caso de uso los invoca. | Baja | pendiente | `application/puertos.py`, `adapters/outbound/integracion.py:15` |
| Patrón Memento | Instantánea y restauración correctas y probadas, sin uso de auditoría/reversión en el flujo. | Baja | pendiente | `domain/existencias/memento.py`, `tests/test_dominio.py` |
| Patrón Caché | Decorador del puerto, invalida al escribir. Conforme. | — | corregido (conforme) | `persistencia.py:36-58` |
| Patrones descartados | No hay CQRS, pipeline ni Specification. | — | conforme | búsqueda en `src/` |
| SOLID/DIP | El dominio no importa infraestructura; puertos pequeños (`IExistenciaRepository`, `Cifrador`, `IEnviarAviso`). Los validadores y manejadores son cohesivos. | — | conforme | `domain/`, `application/puertos.py` |
| DDD | Invariantes y eventos dentro de la raíz; VOs inmutables; agregados no se referencian entre sí (la coordinación va en manejadores). Términos «avoid» del IR ausentes en `src/`. | — | conforme | `existencia.py`, grep de términos |
| Estilo de código | Manejadores en una línea con `;`, importaciones `*`, comparación por nombre de clase en `_publicar_faltante`, doble deduplicación (consumidor + procesador). | Baja | pendiente | `application/manejadores.py`, `integracion.py` |
| ADR | Cada patrón elegido tiene fila y cita clases reales (verificado contra `src/`). Se agregó §9 con el estado real. | — | corregido | `decisiones-arquitectura.md` §4, §9 |
| Seguridad básica | Sin secretos en código; sin SQL; entrada validada. La clave llega por `CIFRADO_CLAVE`, con valor local por defecto si falta. | Baja | pendiente (quitar el valor por defecto en producción) | `seguridad.py:17-20` |
| Evaluación: requisitos cubiertos | Dominio, comandos, eventos, patrones y pruebas herméticas cubiertos. No cubiertos por decisión o límite: persistencia real, outbox transaccional, cifrado en uso. | Media | pendiente | `reference/evaluacion_final.md` |

## Veredicto

**Apto con reservas.** El dominio, los comandos, el ciclo de vida y la política de reposición son correctos y están probados (26 + 8 pruebas en verde) tras corregir dos defectos de severidad alta y tres de media. Las reservas son que PostgreSQL, el outbox transaccional y el cifrado están decididos y modelados, pero no operan en el flujo real.

## Supuestos y límites

- Estado en memoria: reiniciar el servicio pierde los datos; no hay concurrencia transaccional entre procesos.
- Los payloads de eventos son supuestos de diseño (el modelo no define campos).
- La política de reposición crea solicitudes con cantidad 1 y monto 0 (valores por defecto del observador); el modelo no indica cantidad ni monto.
- Las pruebas HTTP usan un cliente ASGI mínimo porque `httpx` no está instalado en el entorno hermético.
- `conformidad.json` lo genera el orquestador y no se tocó; refleja un cálculo anterior a esta revisión.
