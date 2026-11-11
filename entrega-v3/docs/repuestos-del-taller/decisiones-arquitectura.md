# Decisiones de arquitectura — Repuestos del Taller (ADR)

> Documento entregable de la evaluación: argumenta las decisiones **del arquitecto** (no las sustituye).
> Fuente del modelo: IR ArchiMate (`ir.json`) — contexto clasificado **Soporte**, propósito: «Reservar y consumir repuestos por OT y pedir reposición al tocar el mínimo».

## 1. Arquitectura — Hexagonal

**Decisión:** arquitectura hexagonal (puertos y adaptadores) para el servicio de Repuestos del Taller.

**Por qué encaja:** el contexto es de **Soporte**: no contiene la complejidad diferencial del negocio (las paradas y OTs viven en Plan de Mantenimiento e Intervenciones), pero sí reglas propias que deben quedar protegidas de la infraestructura:

- El agregado `Existencia` (con su entidad `ReservaDeRepuesto` y los objetos de valor `StockMinimo`, `Cantidad`, `PlazoDeEntrega`) sostiene invariantes de consistencia fuerte: «reservado ≤ existencia» y «existencia usable = física − reservada» (contrato *Gestión de repuestos del taller*, N3). La regla se materializa en el agregado y se viola con el error `EXISTENCIA_INSUFICIENTE`.
- El agregado `SolicitudDeReposición` impone «una solicitud abierta por referencia» (`SOLICITUD_ABIERTA`) y el nivel de aprobación por monto (`NivelDeAprobacion`: jefe hasta $5 M, gerencia por encima).
- Sobre los agregados se ejecutan **8 comandos** (Registrar entrada, Reservar, Liberar reserva, Confirmar consumo, Ajustar por conteo, Solicitar reposición, Aprobar solicitud, Cancelar solicitud), cada uno con su `…Manejador`, `…Validador` y `…Solicitud` en la capa de aplicación/API.

La hexagonal es la conexión natural con ese nivel de complejidad: el dominio casi sin dependencias y **puertos claros** hacia afuera — repositorios (`IExistenciaRepository`, `ISolicitudDeReposicionRepository`), publicación al bus (`PublicadorDeEventosHttp`), aviso a Notificaciones (`IEnviarAviso` → `EnviarAvisoAdapter`) y cifrado (`Cifrador` → `CifradorAes`). Los adaptadores pueden variar (HTTP, PostgreSQL) sin tocar las invariantes.

**Mezcla con otros dominios:** el modelo define relaciones de *Cliente-Proveedor* hacia abajo (Plan de Mantenimiento e Intervenciones le entregan eventos) y de *Servicio de host abierto / ACL* hacia arriba (Notificaciones, Kardex y compras). La hexagonal aísla esas integraciones en adaptadores y consumidores (`ParadaProgramadaConsumidor`, `OrdenDeTrabajoCerradaConsumidor`) para que las reglas del dominio no se contaminen con los formatos de otros contextos.

## 2. Estilo de servicio — Microservicio

**Justificación del arquitecto** (cita tal cual del registro de decisiones): «microservicio con eventos (reservas y reposición)».
*(La cadena del registro es un marcador de ejemplo; esta redacción es propuesta del asistente, a confirmar.)*

**Qué implica aquí:**

- **Despliegue:** contenedor propio (`Dockerfile`), puerto `5102`, independiente del ciclo de vida de los demás contextos.
- **Datos:** base de datos propia (PostgreSQL `repuestos_del_taller`); ningún otro servicio consulta sus tablas. El stock exige consistencia transaccional local, no distribuida.
- **Integración:** asíncrona por el bus de eventos (publica `Faltante detectado`; consume `Parada programada` y `Orden de trabajo cerrada` según las políticas del IR) y una única API síncrona saliente protegida por ACL (aviso a Notificaciones). Es coherente con el modelo: todas las relaciones del contexto son «Asíncrono», salvo la lectura del catálogo.

## 3. Base de datos — PostgreSQL

**Justificación del arquitecto** (cita tal cual): «PostgreSQL; el stock exige consistencia transaccional».
*(Propuesta del asistente, a confirmar: la justificación registrada es un marcador de ejemplo; el argumento se completa a continuación.)*

**Argumento con la forma del agregado:**

- `Existencia` es una raíz con una **colección de reservas** (`ReservaDeRepuesto`) cuyas invariantes cruzan filas: `Σ reservado ≤ física` y `disponible = física − reservado`. Ese total que cruza filas pide transacciones ACID con bloqueo de fila: PostgreSQL garantiza que dos reservas concurrentes sobre la misma referencia no sobre-comprometan stock.
- El contrato de *Reserva de repuestos* (N4) exige «operación atómica e idempotente; reintentos seguros» y el RNF del servicio es «respuesta < 2 s; trazabilidad de cambios; consistencia fuerte dentro del subdominio». Una BD relacional cubre los tres: transacción + clave de idempotencia (`eventId`) + tabla de outbox con historial.
- El **outbox transaccional** (`BandejaDeSalida`) necesita escribir el evento y el cambio de estado en la misma transacción: solo viable con una BD transaccional como PostgreSQL (DATABASE_URL: `postgresql+psycopg://…`).
- No se necesita flexibilidad documental: los agregados son dos y sus proyecciones (consultas GET de existencia y solicitud) son simples. MongoDB no aportaría nada aquí.

## 4. Patrones

| Patrón | Dominio | Dónde se aplica (clases) | Por qué |
|---|---|---|---|
| Memento | Repuestos del Taller | `ExistenciaMemento`, `SolicitudDeReposicionMemento` (sobre `Existencia` y `SolicitudDeReposicion`) | El RNF del contrato exige «trazabilidad de cambios»: el memento captura el estado interno del agregado sin romper el encapsulamiento, para poder restaurarlo/auditarlo (p. ej. reponer stock tras liberar una reserva o revertir un ajuste por conteo errado). |
| Caché (decorador de repositorio) | Repuestos del Taller | `RepositorioCacheadoExistencia`, `RepositorioCacheadoSolicitudDeReposicion` (decoran `RepositorioExistencia` y `RepositorioSolicitudDeReposicion` detrás de `IExistenciaRepository` e `ISolicitudDeReposicionRepository`) | Las consultas GET (`/api/existencia/{id}`, `/api/solicitud-de-reposicion/{id}`) se repiten desde la UI y la OT; el RNF pide «respuesta < 2 s». El decorador cumple el mismo puerto y deja la escritura sin cachear (el stock es crítico). |
| Cifrado simple de datos personales | Repuestos del Taller | `Cifrador` (puerto de aplicación) y `CifradorAes` (adaptador de infraestructura, clave en `CIFRADO_CLAVE`) | Los datos de contacto/encargado que viajan con los avisos de reposición son personales; se cifran en reposo de forma simple (AES) sin adoptar un PII-framework completo, coherente con un contexto de Soporte. |
| Eventos de integración y consumidores idempotentes | Repuestos del Taller | `RepuestosDelTallerTopicos` (contratos de tópicos), `FaltanteDetectadoTraductor` (traducción evento de dominio → contrato publicado), `ParadaProgramadaConsumidor`, `OrdenDeTrabajoCerradaConsumidor` (idempotentes por `eventId`), `PublicadorDeEventosHttp` (adaptador del bus) | El estilo microservicio integra por eventos: consume `Parada programada` (dispara *Reservar repuesto*) y `Orden de trabajo cerrada` (dispara *Confirmar consumo*) y publica `Faltante detectado` hacia Intervenciones. La entrega es «al menos una vez»: los consumidores deduplican por `eventId` y los reintentos son seguros (contrato N4). |
| Outbox transaccional | Repuestos del Taller | `BandejaDeSalida` (tabla outbox en la misma transacción del agregado) | El evento `Faltante detectado` debe salir **exactamente asociado** al cambio de estado que lo causa: se escribe en la bandeja de salida junto con la existencia/solicitud y un proceso lo publica al bus (`PublicadorDeEventosHttp`); si el servicio cae tras confirmar, el evento no se pierde ni se publica un cambio que nunca ocurrió. |
| Capa anticorrupción (ACL) | Repuestos del Taller | `IEnviarAviso` (puerto, lenguaje propio) y `EnviarAvisoAdapter` (adaptador al simulador de Notificaciones, `/api/notificaciones/enviar-aviso`) | El modelo marca la relación con **Notificaciones** como «Servicio de host abierto + Lenguaje publicado» y con **Kardex y compras** directamente como «Capa anticorrupción» (Archivo/Excel). El servicio no deja que el formato del proveedor (sus avisos, sus planillas) se filtre al dominio: traduce en el adaptador y el dominio solo habla su lenguaje ubicuo. |
| State | Repuestos del Taller | `Existencia` y `SolicitudDeReposicion` (ciclo de vida interno con transiciones validadas) | Decisión del arquitecto: «Existencia y Solicitud de reposición tienen ciclo de vida (disponible → reservado → consumido → bajo mínimo → reponiendo) con transiciones validadas». Los comandos existen solo si el estado lo permite: no se puede liberar una reserva inexistente ni aprobar una solicitud cancelada; el estado inválido levanta la regla de negocio correspondiente. |

### Descartados y por qué

- **CQRS** — Se descarta porque el contexto no tiene un desbalance lecturas/escrituras que lo justifique: son 8 comandos y 2 consultas simples por id (GET de existencia y de solicitud), ambas ya cubiertas por el decorador de caché. CQRS (separación en modelos de lectura/escritura con proyecciones propias) añade dos modelos, sincronización y consistencia eventual a cambio de nada: el RNF pide **consistencia fuerte** dentro del subdominio, justo lo contrario de un modelo de lectura desacoplado. Sí se mantiene la disciplina comando/consulta dentro de la capa de aplicación (un `…Manejador` por comando), que es lo que el modelo necesita.
- **Pipeline de comportamientos (cadena de transversales)** — El pipeline del catálogo (registro → validación → transacción) tiene sentido cuando hay decenas de casos de uso con transversales idénticos y un mediador. Aquí son 8 comandos con validadores dedicados (`RegistrarEntradaDeRepuestoValidador`, `ReservarRepuestoValidador`, …) y la transacción se confirma en el manejador junto con la bandeja de salida; una cadena genérica ocultaría dónde se confirma la transacción (riesgo de doble commit con el outbox) por una ganancia que en este tamaño no existe.
- **Specification** — No hay consultas con combinaciones dinámicas de criterios en el modelo: las únicas lecturas son «existencia por referencia/id» (contrato de *Consulta de existencias*, «solo lectura», error `REFERENCIA_INEXISTENTE`). Las reglas de selección (bajo mínimo, solicitud abierta) son invariantes del agregado, no filtros de consulta: pertencen al State y a las reglas de negocio (`StockMinimoAlcanzadoObservador` → *Solicitar reposición*). Una Specification crearía clases y combinaciones que ningún caso de uso del IR usa.

## 5. Despliegue

- **Contenedor del servicio** (`Dockerfile`, FastAPI/Python): expone `PORT=5102`.
- **Base de datos**: contenedor PostgreSQL propio del dominio; `DATABASE_URL=postgresql+psycopg://forge:forge@postgres:5432/repuestos_del_taller`. La migra/tabla de `BandejaDeSalida` viaja con el servicio.
- **Bus de eventos**: contenedor `event-bus` (5100); `BUS_URL` lo consume `PublicadorDeEventosHttp` (publicar) y la entrega entrante llega por `POST /events/{topic}` con idempotencia (`ProcesadorDeMensajeEntrante`).
- **Simuladores**: contenedor `simulators` (5110) que emula Plan de Mantenimiento, Intervenciones y Notificaciones; `SIMULATORS_URL` lo consume `EnviarAvisoAdapter` (ACL).
- **Gateway** (8080): enruta `/api/repuestos-del-taller/…` al servicio y `/sim/…` a los simuladores; el shell de microfrontends lo compone.
- Todo se levanta con un único `docker compose` del orquestador; las variables (`PORT`, `BUS_URL`, `SIMULATORS_URL`, `CIFRADO_CLAVE`, `DATABASE_URL`) las fija el compose y el servicio solo las lee.

## 6. Microfrontend

- Remote **`mfe-repuestos-del-taller`**, partición **por dominio** (una pantalla por contexto dentro del shell `mfe-shell`).
- El shell lo compone en tiempo de ejecución con **Web Components** (custom elements del remote importados dinámicamente).
- **Filtro por rol dentro del remote**: `Almacenista` ve `RegistrarEntradaDeRepuestoForm`, `LiberarReservaForm`, `AjustarExistenciaPorConteoForm` y `CancelarSolicitudForm`; `Jefe de Operaciones y Mantenimiento` ve `AprobarSolicitudForm`. Los comandos sin rol explícito en el modelo (Reservar, Confirmar consumo) llegan al servicio por eventos, no por pantalla.

## 7. Interoperabilidad con los demás contextos

Detalle de payloads y sobre en `contrato-bus.md` (contract-first; manda sobre los servicios).

- **Publica** (evento de integración real): `repuestos-del-taller.faltante-detectado.v1` — el agregado `Existencia` levanta `FaltanteDetectado` cuando no puede reservar; lo traduce `FaltanteDetectadoTraductor` y sale por el outbox. Intervenciones reacciona poniendo la OT en espera (política del IR: «Faltante detectado → Poner orden en espera»).
- **Consume**:
  - `plan-de-mantenimiento.parada-programada.v1` → `ParadaProgramadaConsumidor` → comando **Reservar repuesto** (relación Cliente-Proveedor, Plan de Mantenimiento upstream). Si falta stock: `EXISTENCIA_INSUFICIENTE` y el propio faltante detectado alimenta el evento publicado.
  - `intervenciones.orden-de-trabajo-cerrada.v1` → `OrdenDeTrabajoCerradaConsumidor` → comando **Confirmar consumo** (Intervenciones upstream, con consumos reales y hora de corte).
  - También escucha `Stock mínimo alcanzado` internamente: la política del IR dispara **Solicitar reposición** desde `StockMinimoAlcanzadoObservador`.
- **APIs síncronas (ACL)**: única salida — **Notificaciones**, API «Enviar aviso» (`IEnviarAviso` / `EnviarAvisoAdapter` → `/api/notificaciones/enviar-aviso` en `SIMULATORS_URL`).
- Relación con **Kardex y compras** (upstream, ACL Archivo/Excel): queda documentada como relación de datos por archivo del modelo; no hay operación síncrona en el contrato del bus, así que el servicio no la materializa por API.

## 8. Riesgos y supuestos

- **Payloads de eventos**: el modelo ArchiMate nombra los eventos pero no sus campos; los campos de `contrato-bus.md` son supuestos de diseño ajustables en `config/event-payloads.json`.
- **Justificaciones del arquitecto**: el registro trae cadenas de ejemplo; se citan tal cual y las completadas se marcan «(propuesta del asistente, a confirmar)».
- **Cifrado simple**: AES con clave simétrica por variable de entorno (`CIFRADO_CLAVE`); es deliberadamente simple — no hay rotación de claves ni cifrado de campo por campo, adecuado para un contexto de Soporte.
- **Ciclo de vida (State)**: el modelo no define la tabla de transiciones completa; se toman transiciones mínimas válidas derivadas de los comandos (reservar → reservado; confirmar consumo → consumido; bajo mínimo → reponiendo tras aprobar y recibir; ver `supuestos.md`).
- **Concurrencia de reservas**: dos paradas simultáneas sobre la misma referencia pueden chocar; la consistencia fuerte de PostgreSQL lo resuelve, pero puede producir `EXISTENCIA_INSUFICIENTE` esperado, que ya tiene trayectoria (evento `Faltante detectado`).
- **Disponibilidad del simulador de Notificaciones**: si cae, el aviso falla; el comando de negocio no se revierte — el aviso es un efecto posterior y los reintentos del bus/ACL deben cubrirlo.

## 9. Estado real de la implementación (revisión S50)

Qué está cableado y qué es solo pieza disponible, para sustentar sin sobrepromesas:

- **Cableado y probado:** State (`EstadoExistencia`, `EstadoSolicitud`), caché (`RepositorioCacheadoExistencia`, `RepositorioCacheadoSolicitudDeReposicion`), consumidores idempotentes (`ParadaProgramadaConsumidor`, `OrdenDeTrabajoCerradaConsumidor`), política *Stock mínimo alcanzado → Solicitar reposición* (`StockMinimoAlcanzadoObservador`, conectada en `RepuestosDelTallerComposicion`) y publicación de `Faltante detectado` por `PublicadorDeEventosHttp`.
- **Disponible pero sin uso en el flujo:** `BandejaDeSalida` (la publicación es directa y en memoria, no transaccional), `Cifrador`/`CifradorAes` (el modelo no almacena datos personales que cifrar), `IEnviarAviso`/`EnviarAvisoAdapter` (ningún caso de uso envía avisos) y `ExistenciaMemento`/`SolicitudDeReposicionMemento` (se usan para serializar y restaurar en pruebas, no para auditoría).
- **Persistencia:** los repositorios son en memoria; `DATABASE_URL` no se lee y no hay driver de PostgreSQL. La decisión de PostgreSQL queda como destino de despliegue, no implementada.
