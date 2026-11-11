# Verificación independiente — Intervenciones (S50)

Revisión externa de `out/services/intervenciones/`, `out/frontend/mfe-intervenciones/` y `out/docs/intervenciones/` frente al modelo ArchiMate (IR), las decisiones del arquitecto y `reference/evaluacion_final.md`.

## Hallazgos

| Criterio | Hallazgo | Severidad | Estado (corregido/pendiente) | Evidencia |
|---|---|---|---|---|
| 1. Decisiones del arquitecto | Lenguaje C# (.NET 8), Clean+DDD, microservicio y MongoDB respetados; los 10 patrones elegidos existen y cumplen su rol. No hay patrones descartados colados (sin Event Sourcing, Saga ni lecturas separadas). | Info | Conforme | `Intervenciones.sln`; `AlmacenDeDocumentosMongo.cs`; `Mediador.cs`; `OrdenDeTrabajoMemento.cs`; `Estados/*`; `Especificaciones/*`; `BandejaDeSalida.cs`; `CifradorAes.cs`; `RepositorioCacheadoOrdenDeTrabajo.cs` |
| 4. ADR | La fila «Cadena de comportamientos» citaba solo validadores, no los comportamientos reales de la cadena. | Media | Corregido | `decisiones-arquitectura.md` §4; `ServiceCollectionExtensions.cs:21-23` (`RegistroComportamiento`, `ValidacionComportamiento`, `TransaccionComportamiento`) |
| 4. ADR | Las filas State y Specification citaban solo la base abstracta y las reglas, sin los estados ni las especificaciones concretas. | Media | Corregido | `Estados/Estado*.cs`; `Especificaciones/Consumo*.cs`, `TareaEjecutadaPor.cs` |
| 4. ADR | El §8 decía que Chain y State «los completan etapas siguientes»; ya estaban implementados. | Baja | Corregido | `decisiones-arquitectura.md` §8 |
| 4. ADR | Todas las clases citadas entre comillas invertidas existen (comprobado por script contra `class/interface/record/struct/enum`). | Info | Conforme | Revisión S50: 0 clases inexistentes |
| 2. SOLID / 3. DDD | Dependencias hacia adentro, verificadas por prueba sobre las referencias de proyecto; el dominio no usa MongoDB ni HTTP. | Info | Conforme | `tests/Intervenciones.Tests/ReglaDeDependenciasTests.cs` |
| 3. DDD | Los eventos los levanta la raíz (`Raise` en cada comando); las colecciones se exponen como `IReadOnlyList`; el estado cambia solo mediante la raíz y la transición se valida antes de mutar. | Info | Conforme | `OrdenDeTrabajo.cs:55-145`, `AggregateRoot.cs:10` |
| 3. DDD | La regla «trabajo mayor exige vuelo de prueba aprobado» es un `if` con `DomainException` dentro de `LiberarDron`, no una regla nombrada como las demás. Es correcto funcionalmente pero inconsistente con el patrón Specification. | Baja | Pendiente (no bloqueante) | `OrdenDeTrabajo.cs:117-118` |
| 3. Lenguaje ubicuo | Ningún término «avoid» del IR para Intervenciones (ticket, solicitud de OT, paso, novedad, visto bueno, etc.) aparece como concepto de dominio. «Solicitud» se usa solo como DTO HTTP/mediador (técnico), «salida» solo en «bandeja de salida». | Info | Conforme | búsqueda sobre `src/**/*.cs` y `mfe-intervenciones/src` |
| 6. Seguridad | La clave llega por `CIFRADO_CLAVE`; sin clave el servicio no arranca. Cifrado AES-GCM con nonce derivado por HMAC (determinista a propósito, para que el documento no cambie si los datos no cambian). No hay secretos en el código ni SQL concatenado (MongoDB con driver tipado). | Info | Conforme | `CifradorAes.cs`; `OpcionesDeMicroservicio.cs:20-23` |
| 6. Seguridad | Sin `MONGO_URL` el servicio cae a un almacén en memoria: útil para pruebas, pero en producción perdería datos en silencio si faltara la variable. El compose la fija siempre. | Baja | Pendiente (límite aceptado) | `BuildingBlocks.Infrastructure/DependencyInjection/ServiceCollectionExtensions.cs:18` |
| 6. Seguridad | La habilitación del técnico se consulta tras la ACL y un fallo del externo produce error, no una decisión implícita. | Info | Conforme | `AsignarTecnicoManejador.cs:15`; `ConsultaDeHabilitacionAdapter.cs` |
| 5. Evaluación final | Cubiertos por las decisiones: patrones argumentados, caché (decorador), estados (memento), cifrado, despliegue (compose), microfrontend web. | Info | Conforme | `decisiones-arquitectura.md` §4-6 |
| 5. Evaluación final | Requisitos que este dominio no puede cubrir solo: «2 dominios en lenguajes diferentes» y «mezclar microservicios y hexagonales» dependen de los otros dominios; aquí el arquitecto decidió arquitectura pura Clean+DDD y microservicio. | Info | Fuera de alcance de este dominio | `decisiones-arquitectura.md` §1-2 |
| 7. Pruebas | Servicio: 68 (BuildingBlocks.Tests) + 120 (Intervenciones.Tests) pasan, 0 fallos. Microfrontend: 25 pruebas vitest pasan; `npm run build` (tsc + vite) correcto. | Info | Conforme | `dotnet test Intervenciones.sln`; `npx vitest run`; `npm run build` |

## Veredicto

**Apto con reservas.** El servicio compila, las 213 pruebas pasan (188 .NET + 25 del microfrontend) y respeta las decisiones vinculantes del arquitecto: lenguaje, arquitectura, estilo, base de datos y los diez patrones elegidos, sin sobreingeniería. Las correcciones de esta revisión fueron solo de documentación (ADR). Las reservas son menores: una regla de negocio sin nombrar y el almacén en memoria como respaldo sin `MONGO_URL`.

## Supuestos y límites

- Las pruebas son herméticas: la transacción real de MongoDB (guardar orden + bandeja de salida) y el bus HTTP no se ejercitaron contra un replica set ni contra el bus real en esta revisión; eso lo cubre el smoke de integración (`smoke/smoke.py`) cuando corre el compose.
- Los campos de los eventos son supuestos de diseño (el modelo nombra los eventos, no su carga útil), documentados en `contrato-bus.md` y `supuestos.md`.
- El cifrado determinista permite igualdad de textos cifrados; es aceptable para «cifrado simple», no para secretos de alta sensibilidad. La rotación de `CIFRADO_CLAVE` está fuera de alcance.
- La caché puede servir datos obsoletos si falla la invalidación; riesgo aceptado por el arquitecto.
- Las justificaciones de lenguaje, arquitectura, estilo y BD del arquitecto son textos de ejemplo; conviene que el equipo las reemplace por las propias antes de sustentar.
- Esta revisión no ejecutó el diferencial contra el `.archimate` crudo; se apoyó en el IR y en `manifest.json`.
