# Verificación independiente — Repuestos del Taller (S50)

Revisor externo. Alcance: `out/services/repuestos-del-taller/`, `out/frontend/mfe-repuestos-del-taller/`, `out/docs/repuestos-del-taller/`.
Pruebas ejecutadas: servicio `pytest` → **60 passed** (incluye 2 nuevas de persistencia SQL en esta pasada); microfrontend `vitest run` → **8 passed**.

| Criterio | Hallazgo | Severidad | Estado (corregido/pendiente) | Evidencia |
|---|---|---|---|---|
| Decisiones: lenguaje, arquitectura, estilo | Python/FastAPI, hexagonal (`domain`/`application`/`adapters`), microservicio con puerto 5102. Coincide con lo decidido. | — | corregido (conforme) | `pyproject.toml`, `adapters/inbound/http/composicion.py` |
| Decisiones: base de datos | Los repositorios eran en memoria y `DATABASE_URL` no se leía. Ahora `_repositorios` elige `RepositorioExistenciaSql`/`RepositorioSolicitudDeReposicionSql` (psycopg) cuando hay `DATABASE_URL`; memoria solo sin ella. Probado contra sqlite3 (sin servidor PostgreSQL disponible: no verificado contra PostgreSQL real). | Alta | corregido (SQL no ejecutado en PostgreSQL) | `composicion.py:28-35`, `persistencia.py:114-170`; pruebas `test_repositorios_sql_persisten_y_restauran_los_agregados`, `test_database_url_selecciona_el_repositorio_sql` |
| Patrón State | Bug: `confirmar_consumo` desde `bajo_minimo`/`reponiendo` lanzaba error **después** de mutar el agregado (física y reservas cambiadas, excepción igualmente). | Alta | corregido | `domain/existencias/estados.py`; prueba `test_consumos_sucesivos_desde_bajo_minimo_no_corrompen_el_agregado` |
| Patrón State | El estado `reponiendo` nunca se alcanzaba (`iniciar_reposicion` sin llamadas). | Media | corregido | `AprobarSolicitudManejador._iniciar_reposicion`; prueba `test_aprobar_la_solicitud_pone_la_existencia_en_reponiendo` |
| Política del IR «Stock mínimo alcanzado → Solicitar reposición» | `StockMinimoAlcanzadoObservador` existía pero no estaba conectado: la política nunca se ejecutaba. | Alta | corregido | `ConfirmarConsumoManejador._notificar_stock_minimo`, `composicion.py`; prueba `test_stock_minimo_alcanzado_dispara_solicitar_reposicion` |
| Eventos de integración | La ruta HTTP de reservar usaba un manejador sin publicador: el `Faltante detectado` no salía al bus. Ahora un único manejador compartido. | Media | corregido | `composicion.py`; prueba `test_reservar_por_http_publica_el_faltante` |
| Validación de entrada | Un cuerpo inválido (campos faltantes, UUID mal formado) producía 500 o 404 (`ValueError`→404). Ahora 422. | Media | corregido | `adapters/inbound/http/endpoints.py`; prueba `test_cuerpo_invalido_responde_422_y_no_500` |
| Patrón Outbox | `BandejaDeSalida` sí está en la ruta de producción (`PublicadorConBandeja`, `composicion.py:43`), pero es en memoria: no es transaccional con el agregado y descarta tras 3 reintentos. | Media | pendiente (requiere tabla outbox en la misma transacción) | `integracion.py:48-80`, `composicion.py:43` |
| Patrón Cifrado | Instanciado en producción (`composicion.py:43`) y usado por `BandejaDeSalida` al guardar cada evento. Se eliminó el fallback XOR+HMAC: ahora siempre AES-GCM (`cryptography` declarada). | Media | corregido | `seguridad.py:13-27`, `composicion.py:43`, `integracion.py:48-57` |
| Patrón ACL | `EnviarAvisoAdapter` se instancia en `composicion.py:45` y lo invoca `StockMinimoAlcanzadoObservador` (`application/integracion.py:86`). Conforme. | — | corregido (conforme) | `composicion.py:45`, `integracion.py:86` |
| Patrón Memento | Ahora participa en producción: los repositorios SQL guardan `crear_memento` y reconstruyen con `restaurar_desde`; los endpoints serializan el memento. No hay reversión/auditoría de estados anteriores. | Baja | corregido (rol de persistencia) | `persistencia.py:129,132,153,162`, `endpoints.py:17` |
| Patrón Caché | Decorador del puerto, invalida al escribir. Conforme. | — | corregido (conforme) | `persistencia.py:36-58` |
| Patrones descartados | No hay CQRS, pipeline ni Specification. | — | conforme | búsqueda en `src/` |
| SOLID/DIP | El dominio no importa infraestructura; puertos pequeños (`IExistenciaRepository`, `Cifrador`, `IEnviarAviso`). Los validadores y manejadores son cohesivos. | — | conforme | `domain/`, `application/puertos.py` |
| DDD | Invariantes y eventos dentro de la raíz; VOs inmutables; agregados no se referencian entre sí (la coordinación va en manejadores). Términos «avoid» del IR ausentes en `src/`. | — | conforme | `existencia.py`, grep de términos |
| Estilo de código | Manejadores en una línea con `;`, importaciones `*`, comparación por nombre de clase en `_publicar_faltante`, doble deduplicación (consumidor + procesador). | Baja | pendiente | `application/manejadores.py`, `integracion.py` |
| ADR | Cada patrón elegido tiene fila y cita clases reales (verificado contra `src/`). Se agregó §9 con el estado real. | — | corregido | `decisiones-arquitectura.md` §4, §9 |
| Seguridad básica | Sin secretos en código; SQL parametrizado (`%s`; el único f-string interpola constantes internas, no entrada). Entrada validada. La clave llega por `CIFRADO_CLAVE`, con valor local derivado si falta. | Baja | pendiente (exigir la clave en producción) | `persistencia.py:125-135`, `seguridad.py:17-20` |
| Evaluación: requisitos cubiertos | Caché, estados/mementos, cifrado, persistencia SQL, eventos y pruebas cubiertos. Límite: outbox transaccional, y el despliegue con PostgreSQL real no se pudo ejecutar aquí. Lenguaje distinto, mezcla de arquitecturas y BD por dominio responden a decisiones del arquitecto. | Media | pendiente | `reference/evaluacion_final.md:41` |

## Veredicto

**Apto con reservas.** El dominio, los comandos, el ciclo de vida y la política de reposición son correctos y están probados (60 + 8 pruebas en verde) tras corregir tres defectos de severidad alta y varios de media. Las reservas: el outbox sigue en memoria (no transaccional) y la persistencia PostgreSQL se probó solo con sqlite3, no contra un servidor PostgreSQL.

## Supuestos y límites

- Con `DATABASE_URL` los agregados sobreviven al reinicio; sin ella (solo test) viven en memoria. La concurrencia entre procesos no usa bloqueo de fila: dos reservas simultáneas podrían pisarse (último en guardar gana).
- La `BandejaDeSalida` es en memoria: un evento pendiente se pierde si el proceso cae.
- Los payloads de eventos son supuestos de diseño (el modelo no define campos).
- La política de reposición crea solicitudes con cantidad 1 y monto 0 (valores por defecto del observador); el modelo no indica cantidad ni monto.
- Las pruebas HTTP usan un cliente ASGI mínimo porque `httpx` no está instalado en el entorno hermético.
- `conformidad.json` lo genera el orquestador y no se tocó; refleja un cálculo anterior a esta revisión.
