# Decisiones de arquitectura — Intervenciones

Contexto **Intervenciones** (clasificación en el modelo: **Core**). Propósito: «Ejecutar, liberar y cerrar el trabajo de mantenimiento dejando evidencia verificable». Agregado único: **Orden de trabajo** (`OrdenDeTrabajo`), con 9 comandos. Decisiones tomadas por el arquitecto; este documento las argumenta con evidencia del modelo.

## 1. Arquitectura — Clean + DDD (C#)

**Decisión:** Clean Architecture con DDD táctico, en C# (.NET 8). Justificación del arquitecto: Clean+DDD por la riqueza de reglas del agregado Orden de trabajo; C# por tipado fuerte y soporte de DDD.

**Por qué encaja:**
- El contexto es **Core**: concentra reglas propias del negocio, no soporte genérico. Las reglas están en los contratos: `ORDEN_CERRADA_INMUTABLE`, `PARADA_INEXISTENTE`, `SERIE_FALTANTE`, `LIBERA_EL_MISMO_QUE_EJECUTO` (y `PRUEBA_DE_VUELO_PENDIENTE` en el contrato de ejecución y liberación).
- `OrdenDeTrabajo` es una raíz con entidades (`TareaEjecutada`, `ConsumoDeRepuesto`, `Liberacion`) y objetos de valor (`TipoDeOrden`, `EstadoDeLaOrden`, `Hallazgo`, `HorasHombre`, `HoraDeCorte`, `VueloDePrueba`). Las invariantes viven en la raíz y los 9 comandos la modifican solo a través de ella.
- Capas con dependencias hacia adentro: **dominio** (agregado, eventos, reglas, puerto `IOrdenDeTrabajoRepository`), **aplicación** (comandos, consultas, manejadores, validadores, puertos `IConsultaDeHabilitacion` y `Cifrador`), **infraestructura** (`RepositorioOrdenDeTrabajo`, `CifradorAes`, `PublicadorDeEventosHttp`, `ConsultaDeHabilitacionAdapter`) y **API** (`IntervencionesEndpoints`, `IntervencionesComposicion`).

**Qué se mezcla con otros dominios y por qué:** la arquitectura interna es pura Clean+DDD; lo que se «mezcla» es solo en las fronteras, y solo por contrato:
- Con **Plan de Mantenimiento** (cliente-proveedor): consume el evento `Parada programada`, que dispara el comando `Abrir orden de trabajo`.
- Con **Repuestos del Taller**: consume `Faltante detectado`, que dispara `Poner orden en espera`; recibe de él, a su vez, el cierre de la OT.
- Con **Habilitación de Personal** (servicio de host abierto, síncrono): consulta de habilitación del técnico, aislada tras una capa anticorrupción.
- Con **Flota y Componentes**, **Plan de Mantenimiento**, **Repuestos del Taller** e **Indicadores**: publica `Orden de trabajo cerrada`.

## 2. Estilo de servicio — Microservicio

**Decisión:** microservicio autónomo con su propia base de datos; se integra por eventos (bus) y APIs. Justificación del arquitecto: microservicio con eventos; consume y publica eventos del ciclo de la OT.

- **Despliegue:** un contenedor propio (puerto 5101), configurado solo por variables de entorno (`PORT`, `BUS_URL`, `SIMULATORS_URL`, `CIFRADO_CLAVE`, `MONGO_URL`).
- **Datos:** base propia; ningún otro contexto lee sus colecciones. Los demás se enteran del cierre de una OT por el evento, no por la base.
- **Integración:** asíncrona con el bus (tres tópicos: uno publicado, dos consumidos) y una API síncrona hacia Habilitación de Personal. Todas las relaciones del modelo con este contexto son «Asíncrono» salvo la consulta de habilitación.
- **Por qué aquí:** las relaciones del modelo ya son cliente-proveedor por evento; el contexto tiene un ciclo de vida de cambio distinto (taller) del de la planificación y del inventario.

## 3. Base de datos — MongoDB

**Decisión:** MongoDB (replica set de un nodo). Justificación del arquitecto: el agregado se guarda como documento (memento) con transacciones en replica set.

- **Forma del agregado:** `OrdenDeTrabajo` incluye sus tareas, consumos, hallazgos, vuelos de prueba y liberación; se lee y escribe **completa**, como una unidad. Un documento por orden coincide con el límite de consistencia del agregado, sin joins ni mapeo relacional.
- **Consistencias que exige:**
  - Concurrencia sobre una misma orden (varios técnicos registrando tareas y consumos): control optimista con versión en el documento.
  - Atomicidad entre guardar el agregado y registrar el evento a publicar: **transacción multi-documento** (replica set) que escribe orden y `BandejaDeSalida` a la vez.
  - Idempotencia de entrada: colección de mensajes procesados por `eventId`.
- **Persistencia como memento:** el documento es la serialización de `OrdenDeTrabajoMemento`, de modo que el dominio no conoce el esquema de Mongo.

## 4. Patrones

| Patrón | Dominio | Dónde se aplica (clases) | Por qué |
|---|---|---|---|
| CQRS con mediador | Intervenciones | `AbrirOrdenDeTrabajoComando`, `AbrirOrdenDeTrabajoManejador`, `LiberarDronComando`, `LiberarDronManejador`, `CerrarOrdenDeTrabajoComando`, `CerrarOrdenDeTrabajoManejador`, `ObtenerOrdenDeTrabajoConsulta`, `ObtenerOrdenDeTrabajoManejador` (y los análogos de los demás comandos) | Hay 9 comandos con reglas distintas y una lectura frecuente (el shell del microfrontend); separarlos evita que la lectura cargue con la lógica de escritura y deja un manejador por caso de uso. |
| Cadena de comportamientos (Chain of Responsibility) | Intervenciones | `IComportamientoDePipeline`, `RegistroComportamiento`, `ValidacionComportamiento`, `TransaccionComportamiento` (cadena ejecutada por `Mediador` en ese orden), más un validador por comando (`AbrirOrdenDeTrabajoValidador`, `AsignarTecnicoValidador`, `CerrarOrdenDeTrabajoValidador`, …) que `ValidacionComportamiento` invoca antes del manejador | Validación, y preocupaciones transversales, se aplican en orden y sin tocar los manejadores; las precondiciones de los contratos se rechazan antes de llegar al dominio. |
| Memento | Intervenciones | `OrdenDeTrabajoMemento`, `OrdenDeTrabajo`, `RepositorioOrdenDeTrabajo` | Permite guardar y restaurar el estado del agregado como documento sin exponer su interior ni acoplar el dominio a MongoDB. |
| State | Intervenciones | `OrdenDeTrabajo`, `EstadoDeLaOrden`, `EstadoAbierta`, `EstadoEnEjecucion`, `EstadoEnEspera`, `EstadoEjecutada`, `EstadoLiberada`, `EstadoCerrada` | La orden pasa por estados (abierta, en espera, cerrada, …) y qué comandos admite depende del estado; `ORDEN_CERRADA_INMUTABLE` es el caso límite: una orden cerrada rechaza toda modificación. |
| Specification | Intervenciones | `Especificacion`, `ConsumoRequiereSerie`, `ConsumoConSerieInstalada`, `TareaEjecutadaPor`, y las reglas `OrdenCerradaInmutable`, `ParadaInexistente`, `SerieFaltante`, `LiberaElMismoQueEjecuto` | Cada regla de negocio de los contratos es una especificación nombrada, componible y probable de forma aislada. |
| Eventos de integración y consumidores idempotentes | Intervenciones | `OrdenDeTrabajoCerradaV1`, `IntervencionesTopicos`, `ParadaProgramadaConsumidor`, `FaltanteDetectadoConsumidor`, `ProcesadorDeMensajeEntrante` | El bus entrega al menos una vez; los consumidores deduplican por `eventId` para que un reintento no abra dos órdenes ni ponga dos veces en espera. |
| Outbox transaccional | Intervenciones | `BandejaDeSalida`, `PublicadorDeEventosHttp`, `RepositorioOrdenDeTrabajo` | `Orden de trabajo cerrada` debe publicarse si y solo si la orden se guardó; la transacción de MongoDB escribe ambos y el publicador reintenta desde la bandeja. |
| Capa anticorrupción (ACL) | Intervenciones | `IConsultaDeHabilitacion`, `ConsultaDeHabilitacionAdapter`, `OrdenDeTrabajoCerradaTraductor` | Aísla el modelo propio del de Habilitación de Personal (consulta síncrona) y traduce el evento interno al contrato público `OrdenDeTrabajoCerradaV1`. |
| Cifrado simple de datos personales | Intervenciones | `Cifrador`, `CifradorAes` | El contrato exige datos de personas bajo la Ley 1581/2012 (técnico asignado, firma de liberación); se cifran con clave de `CIFRADO_CLAVE` tras un puerto. |
| Caché (decorador de repositorio) | Intervenciones | `RepositorioCacheadoOrdenDeTrabajo`, `IOrdenDeTrabajoRepository`, `RepositorioOrdenDeTrabajo` | Decorador de repositorio de lectura sobre Orden de trabajo: el shell del microfrontend consulta la OT con frecuencia y la caché se invalida al escribir. |

### Descartados y por qué

Ningún patrón del catálogo fue descartado por el arquitecto: los diez están elegidos. Quedan fuera, por no estar en el catálogo de decisiones, estas alternativas (propuesta del asistente, a confirmar):
- **Event Sourcing:** no hace falta; el modelo exige guardar el estado final de la OT y su evidencia, no reconstruir historia por eventos, y añadiría complejidad de proyecciones.
- **Saga / orquestación distribuida:** el contexto no coordina transacciones entre servicios; cada reacción (abrir, poner en espera) es una acción local.
- **Bases de lectura separadas (CQRS completo):** la carga de lectura se resuelve con la caché; una réplica de lectura sería prematura.

## 5. Despliegue

Orquestado con `docker compose`:
- **intervenciones:** contenedor propio (`Dockerfile`), puerto 5101.
- **mongodb:** replica set de un nodo (necesario para transacciones); URL en `MONGO_URL`.
- **event-bus:** bus de eventos (`BUS_URL`, publica en `/publish`; el servicio recibe en `/events/{topic}`).
- **simulators:** simulan los contextos no construidos (Plan de Mantenimiento, Repuestos del Taller, Habilitación de Personal, etc.); `SIMULATORS_URL`.
- **gateway:** `http://localhost:8080`; `/api/<servicio>/…` va a los servicios reales y `/sim/…` a los simuladores.

## 6. Microfrontend

Remote **`mfe-intervenciones`**: un microfrontend por dominio (partición por dominio), no por rol; dentro, el filtro por rol decide qué formularios se muestran (técnico de mantenimiento ejecuta y libera; Almacenista y Jefe de Operaciones y Mantenimiento consultan y aprueban). Se empaqueta como Web Component, cargado en tiempo de ejecución por el shell, que consulta la OT con frecuencia (de ahí la caché). Incluye un formulario por cada comando de escritura relevante (asignar técnico, registrar ejecución, consumo, hallazgo, vuelo de prueba, liberar, cerrar).

## 7. Interoperabilidad con los demás contextos

Detalle en `contrato-bus.md`. Resumen:

| Tópico | Sentido | Contraparte | Efecto |
|---|---|---|---|
| `plan-de-mantenimiento.parada-programada.v1` | Consume | Plan de Mantenimiento | Abre la orden de trabajo |
| `repuestos-del-taller.faltante-detectado.v1` | Consume | Repuestos del Taller | Pone la orden en espera |
| `intervenciones.orden-de-trabajo-cerrada.v1` | Publica | Flota y Componentes, Plan de Mantenimiento, Repuestos del Taller, Indicadores | Consumos reales, horas-hombre y componentes con su hora de corte |

API síncrona: consulta de habilitación en Habilitación de Personal (`/api/habilitacion-de-personal/consulta-de-habilitacion`), tras la ACL.

## 8. Riesgos y supuestos

- Los **campos de los eventos son supuestos de diseño**: el modelo nombra los eventos pero no define su carga útil (ver `contrato-bus.md`).
- Entrega al menos una vez: si el almacén de idempotencia falla, un evento puede procesarse dos veces; mitigado con clave por `eventId`.
- Dependencia de transacciones: MongoDB debe correr como replica set; sin él, la bandeja de salida pierde atomicidad.
- La clave de cifrado llega por entorno (`CIFRADO_CLAVE`); su rotación queda fuera de alcance.
- La caché puede servir datos obsoletos si la invalidación falla; es un riesgo aceptado porque solo cachea lecturas y se invalida al escribir.
- Las justificaciones de lenguaje, arquitectura, estilo y base de datos del arquitecto son textos de ejemplo; este documento las complementa con evidencia del modelo (a confirmar por el arquitecto).
- La cadena de comportamientos y los estados ya están implementados con las clases citadas en la tabla de patrones (verificado en S50).
