# 11 · Las decisiones de cada servicio: qué se eligió y la justificación registrada

Este documento reúne, **servicio por servicio**, lo que el arquitecto decidió y **por qué**. El texto completo de cada justificación está en
`archiforge/decisiones/<servicio>.toml` (y viaja con el producto en `entrega-v3/docs/<servicio>/decisiones.toml`); aquí se resume para exponerlo.

**Cómo está escrita cada justificación:** primero la **razón** (ligada a un requisito del diseño o a algo comprobado en el código), después la **alternativa descartada**
y al final el **costo que se acepta**. Las claves que se citan (H-22, D-11, D-18…) son los hallazgos y decisiones de `diseno/Fase00/05_analisis_hallazgos.md` y de `docs/decisiones.md`.

---

# A · Intervenciones (órdenes de trabajo)

> Contexto **Core** · C# · Clean + DDD · microservicio · MongoDB

## Las cuatro decisiones principales

| Decisión | Por qué (resumen) | Alternativa descartada | Costo aceptado |
|---|---|---|---|
| **Lenguaje: C# (.NET 8)** | La orden concentra las reglas más delicadas del taller: *quien ejecuta no libera* en trabajos mayores (**H-22**) y **vuelo de prueba aprobado de 5 a 10 min** (**H-23**). El tipado fuerte hace que el compilador rechace estados y valores inválidos antes de ejecutar | Python: aquí hay más reglas que datos. Java: equivalente, pero con C# y Python el producto muestra el mismo modelo en un lenguaje tipado y en uno dinámico | Mantener dos ecosistemas |
| **Arquitectura: Clean + DDD** | El valor está en el agregado *Orden de trabajo* (seis estados, reglas con nombre, firmas distintas). El dominio **no depende** de MongoDB, del bus ni de HTTP: las reglas se prueban sin infraestructura y la base o el bus se pueden cambiar sin tocarlas | Arquitectura en capas clásica: deja que la base de datos dicte el modelo | Más clases e interfaces |
| **Estilo: microservicio** | Contexto con dueño y ritmo propios que **debe seguir operando** aunque Repuestos o Plan estén caídos; en campo la conectividad no es estable (**D-18**). Se relaciona solo por eventos y no comparte base de datos | SOA con orquestador (el flujo se resuelve con eventos simples); monolito modular (no mostraría la comunicación entre servicios) | Consistencia eventual con otros contextos |
| **Base de datos: MongoDB (réplicas)** | La orden se lee y se guarda **como una unidad** (tareas, consumos, hallazgos, vuelo de prueba, firmas): un documento la representa sin partirla en tablas; el memento *es* ese documento. Las réplicas permiten las **transacciones** que necesita el outbox | PostgreSQL: fragmentaría el agregado en varias tablas | Operar un conjunto de réplicas; versión optimista (409 ante escrituras simultáneas) |

## Los diez patrones

| Patrón | Por qué se usa aquí | Costo aceptado |
|---|---|---|
| **CQRS con mediador** | 9 comandos con reglas y validaciones distintas; las lecturas devuelven una forma plana (DTO) distinta del agregado. El mediador evita que los endpoints conozcan los casos de uso | Varias clases por operación |
| **Pipeline** | Los contratos exigen operaciones **atómicas e idempotentes con reintentos seguros**; la cadena Registro → Validación → Transacción impide que un caso de uso olvide validar o confirmar | El flujo es más difícil de seguir si no se conoce la cadena |
| **Memento** | El agregado debe guardarse y reconstruirse **sin que el dominio conozca MongoDB**; al restaurar se vuelve a validar | Un record por agregado |
| **State** | Ciclo de vida con reglas: *Abierta, En espera, En ejecución, Ejecutada, Liberada, Cerrada*; una orden cerrada es inmutable. Las reglas viven en un solo lugar | Una clase por estado (con 2-3 estados bastaría un enum) |
| **Specification** | Condiciones **combinables y reutilizables** (un repuesto exige serie, el consumo tiene serie instalada, una tarea la ejecutó una persona) que componen reglas como `SERIE_FALTANTE` | Una clase por condición |
| **Outbox** | Al cerrar la orden hay que avisar a Repuestos (**D-11**) sin perder el aviso: orden y mensaje se guardan en **la misma transacción**; un despachador publica con reintentos | Una colección de bandeja y un despachador |
| **Eventos + consumidores idempotentes** | El diseño define como **asíncronas** las relaciones con Plan, Repuestos, Flota e Indicadores. Contratos versionados (V1) e idempotencia por `eventId` porque la entrega es *al menos una vez* | Consistencia eventual |
| **ACL** | La habilitación del técnico es un dato de **otro contexto**: un puerto y un adaptador lo traducen a sí/no; con tiempo máximo y **503** si el otro falla | Un puerto y un adaptador por API externa |
| **Caché** | Las pantallas consultan la orden con frecuencia y los datos cambian poco entre operaciones; se invalida al escribir | Política de invalidación; caché por instancia |
| **Cifrado** | La orden registra **datos de personas** (técnicos y firmas) y el contrato exige protegerlos (**Ley 1581 de 2012**). AES-256-GCM autentica además el dato | Clave por variable de entorno, sin rotación; cifrado determinista |

---

# B · Repuestos del Taller (almacén)

> Contexto **Soporte** · Python · Hexagonal · microservicio · PostgreSQL

## Las cuatro decisiones principales

| Decisión | Por qué (resumen) | Alternativa descartada | Costo aceptado |
|---|---|---|---|
| **Lenguaje: Python (FastAPI)** | Dominio **acotado** (existencias, reservas, reposición) que se beneficia de iterar rápido; FastAPI da validación y rutas con poco código. Aporta el **contraste** con Intervenciones | C#/Java: válidos, pero más ceremonia para un dominio pequeño | Menos comprobación en compilación (se compensa con pruebas y compuertas) |
| **Arquitectura: Hexagonal** | Repuestos conversa con varias cosas externas (**base, bus, avisos**) y cada una es un **puerto con adaptador intercambiable**; el núcleo no importa infraestructura | Clean + DDD completo: las reglas propias son pocas (`EXISTENCIA_INSUFICIENTE`, `SOLICITUD_ABIERTA`, nivel de aprobación por monto) | Más interfaces que un CRUD simple |
| **Estilo: microservicio con eventos** | **Reserva inmediata y consumo eventual (D-11)**: una transacción modifica un solo agregado. Reserva al conocer la parada y descuenta al llegar «Orden de trabajo cerrada». Si Intervenciones cae, el stock no se corrompe | Llamadas directas entre servicios (acoplamiento temporal) | El stock se descuenta unos instantes después de cerrar la orden |
| **Base de datos: PostgreSQL** | Las existencias exigen **consistencia estricta**: lo reservado no supera la existencia y la existencia usable es física − reservado; transacciones relacionales y claves únicas son la base natural para sostenerlo | MongoDB: la flexibilidad documental aporta menos que las restricciones relacionales | Una segunda tecnología de base de datos. **Límite reconocido y comprobado:** con una instancia las reservas simultáneas son correctas; con dos réplicas se pierden actualizaciones (no hay control de versión ni bloqueo de fila), por lo que hoy debe correr como una sola instancia |

## Los siete patrones

| Patrón | Por qué se usa aquí | Costo aceptado |
|---|---|---|
| **Memento** | `Existencia` y `Solicitud de reposición` se guardan como fotografía inmutable en JSON dentro de PostgreSQL; el dominio no conoce la base | Un record por agregado |
| **State** | La existencia (*disponible → reservado → consumido → bajo mínimo → reponiendo*) y la solicitud (*abierta → aprobada/cancelada*) tienen transiciones validadas; reglas como «solo se aprueba una solicitud abierta» viven en un solo lugar | Una clase por estado |
| **Caché** | Las consultas de existencia y de solicitud son las lecturas más frecuentes de las pantallas del almacén; decorador con vencimiento de 60 s, invalidado al guardar | Política de invalidación; caché por instancia |
| **Cifrado** | Repuestos **casi no maneja datos personales**: se aplica a la **bandeja de eventos pendientes** (ids de órdenes, drones y repuestos) por política del proyecto y como defensa en profundidad | Clave por variable de entorno, sin rotación |
| **Eventos + consumidores idempotentes** | Recibe «Parada programada» y «Orden de trabajo cerrada», publica «Faltante detectado». Idempotencia por `eventId`: **descontar dos veces el stock sería un error de negocio** | Consistencia eventual |
| **Outbox** | «Faltante detectado» **no puede perderse**: es lo que pone en espera la orden. Se guarda cifrado y durable en PostgreSQL antes de enviarse, con reintentos | **Límite reconocido:** el evento no comparte transacción con el agregado; el generador ya trae un esqueleto transaccional |
| **ACL** | Los avisos van a un sistema externo de notificaciones; el puerto `IEnviarAviso` traduce la llamada con tiempo máximo y, si falla, **la solicitud no se revierte** | Un puerto y un adaptador |

---

# C · Lo que conviene decir en voz alta

1. **Las razones salen del negocio, no del gusto.** Cada elección se apoya en una regla del diseño (H-22, H-23, D-11, D-18…) o en un requisito de los contratos (operaciones atómicas e idempotentes, Ley 1581).
2. **Cada servicio tiene su propia razón.** La arquitectura, el lenguaje y la base de Intervenciones y de Repuestos son distintos **a propósito** y por motivos distintos: reglas ricas y un agregado grande frente a un dominio acotado con consistencia de stock.
3. **Los costos están a la vista.** Cada justificación termina con lo que se acepta a cambio, y dos de ellas reconocen un límite concreto (la concurrencia fina en Repuestos y el outbox no transaccional).
4. **La herramienta las exige.** Con la política `require_justifications`, un servicio con justificaciones vacías o de ejemplo **no se ensambla**.

---
Anterior: [10 · Glosario](10-glosario.md) · Volver al [índice](README.md)
