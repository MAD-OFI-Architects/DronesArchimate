# 10 · Glosario: las palabras, explicadas para todos

Ordenado alfabéticamente. Cada definición intenta ser comprensible **sin conocer informática**, con un ejemplo cotidiano cuando ayuda.

---

**ACL (Capa anticorrupción)** — Un "intérprete" entre dos sistemas que hablan idiomas distintos. Evita que el vocabulario de uno **contamine** al otro. *Ejemplo: el servicio no ve el formato de Habilitación de Personal; el intérprete le entrega solo "sí" o "no".*

**ADR (Registro de decisión de arquitectura)** — Un documento corto que dice **qué se decidió, por qué y qué alternativas se descartaron**. El programa genera uno por servicio.

**Agente (de IA)** — El programa de inteligencia artificial que **escribe el código** de cada etapa. Trabaja con órdenes de trabajo precisas y sus resultados pasan por compuertas.

**Agregado** — Un grupo de objetos del negocio que **siempre cambian juntos** y que se tratan como una unidad con reglas propias. *Ejemplo: la "Orden de trabajo" con sus tareas, consumos y hallazgos.*

**API** — La "ventanilla" de un servicio: las operaciones que ofrece para que otros lo usen. *Ejemplo: "abrir una orden de trabajo".*

**ArchiMate** — Lenguaje estándar para dibujar organizaciones: qué hace, con qué sistemas y por qué. Se usa con la herramienta **Archi**.

**Asíncrono** — Que **no espera la respuesta**. Se manda un aviso y se sigue. Lo contrario es **síncrono** (se pregunta y se espera). *Ejemplo: dejar un mensaje en un buzón vs. llamar por teléfono.*

**Bandeja de entrada (inbox)** — Registro de los mensajes **ya procesados**, para no procesar dos veces el mismo.

**Bandeja de salida (outbox)** — Registro de los mensajes **pendientes de enviar**, guardados junto con el cambio de negocio, para no perder avisos.

**Broker** — El "buzón central" que recibe mensajes y los entrega a quien corresponde. *Ejemplo: RabbitMQ.*

**Caché** — Una memoria de corto plazo que guarda lo consultado hace poco para responder más rápido sin volver a buscarlo.

**Cifrado** — Convertir un dato en algo ilegible sin la clave. Protege la información personal si alguien accede a la base de datos.

**Clean Architecture** — Forma de organizar un servicio en **capas concéntricas** donde lo importante (las reglas del negocio) está en el centro y no depende de la tecnología.

**Comando** — Una **acción que se pide** al sistema y que cambia algo. *Ejemplo: "liberar el dron".*

**Compuerta (gate)** — Una **revisión automática** que el código debe pasar antes de seguir. *Ejemplo: "¿existe todo lo que el modelo pide?".*

**Conformidad** — El porcentaje de lo que el modelo pide que **realmente existe en el código**.

**Consistencia eventual** — Los datos de dos servicios **terminan coincidiendo**, pero no al mismo instante. *Ejemplo: el stock se descuenta unos instantes después de cerrar la orden.*

**Consulta** — Una pregunta que **solo lee** y no cambia nada. Lo opuesto a un comando.

**Contenedor (Docker)** — Una "caja" que lleva una aplicación con todo lo que necesita, de modo que funcione igual en cualquier computadora.

**Contexto delimitado (bounded context)** — Un "departamento" del software, con su propio vocabulario y reglas, separado de los demás. *Ejemplo: "Intervenciones" y "Repuestos del Taller".*

**Contrato** — El acuerdo escrito sobre **qué ofrece un servicio y qué errores puede dar**. También, la forma exacta de un evento.

**CQRS** — Patrón que **separa** las acciones que cambian datos de las consultas que los leen.

**Cola de mensajes muertos (dead letter queue, DLQ)** — Donde se guardan los mensajes que **no se pudieron entregar** tras varios intentos, para revisarlos y reprocesarlos sin perderlos.

**DDD (Domain-Driven Design)** — Una forma de diseñar software **centrada en el negocio**: usar su vocabulario, partirlo en contextos y modelar sus reglas.

**Decorador** — Un objeto que **envuelve a otro** para añadirle algo (caché, cifrado) sin cambiarlo.

**Despachador** — El proceso que **toma los mensajes pendientes** de la bandeja de salida y los envía.

**DTO** — Un objeto plano con los datos que necesita una pantalla, distinto del objeto interno del negocio.

**Entidad** — Un objeto del negocio con **identidad propia** (dos órdenes con los mismos datos siguen siendo distintas).

**Evento de dominio** — Un **hecho ya ocurrido** dentro de un servicio. *Ejemplo: "Orden de trabajo abierta".*

**Evento de integración** — Un evento de dominio **publicado para otros servicios**, con formato versionado. *Ejemplo: `intervenciones.orden-de-trabajo-cerrada.v1`.*

**Gateway (API Gateway)** — La **puerta de entrada** única: recibe las peticiones del navegador y las envía al servicio correcto.

**Hexagonal (arquitectura)** — Organización con un núcleo de negocio rodeado de **puertos** (por donde entran y salen cosas) y **adaptadores** (que conectan con la tecnología concreta).

**Idempotente** — Que **repetirlo no cambia el resultado**. *Ejemplo: apretar dos veces el botón del ascensor no llama a dos ascensores.*

**Interoperabilidad** — La capacidad de que sistemas distintos, hechos con tecnologías distintas, **se entiendan y trabajen juntos** sin conocerse por dentro.

**IR (representación intermedia)** — El **resumen compacto** del modelo ArchiMate que el programa genera para trabajar (el archivo original pesa 1,3 MB).

**Lenguaje ubicuo** — El **vocabulario común** del negocio, usado igual en el diseño y en el código. *Ejemplo: se dice "orden de trabajo", no "ticket".*

**Manifiesto** — La **lista de todo lo que debe existir** en el código, derivada del modelo y de las decisiones.

**Mediador** — Un intermediario que recibe un pedido y lo **entrega al responsable**, para que quien pide no conozca a quien atiende.

**Memento** — Patrón que toma una **fotografía** del estado de un objeto para guardarlo y reconstruirlo después.

**Microfrontend** — Una **parte independiente** de la interfaz web, hecha y desplegada por separado.

**Microservicio** — Un servicio **pequeño y autónomo**, con su propia base de datos, que se comunica con otros por la red.

**Monolito** — Una sola aplicación grande que contiene todo.

**Orquestador (runner)** — La pieza del programa que **ejecuta las etapas en orden**, lleva la cuenta y reintenta.

**Outbox** — Ver *Bandeja de salida*.

**Patrón de diseño** — Una **receta probada** para un problema que se repite al programar.

**Pipeline** — Una **cadena de pasos** por los que pasa cada petición (registro → validación → transacción).

**Política (en el modelo)** — Una regla "**cuando ocurre X, hacer Y**". *Ejemplo: cuando se programa una parada, abrir una orden.*

**Problem Details** — Un **formato estándar** para describir errores de una API, con título, detalle y datos extra.

**Puerto / Adaptador** — El puerto es una **interfaz** que dice qué se necesita; el adaptador es quien **la cumple** con una tecnología concreta.

**RabbitMQ** — El *broker* usado: recibe mensajes, los guarda en colas y los entrega a los suscriptores, con reintentos.

**Raíz (del agregado)** — El objeto **principal** de un agregado, por el que se accede a todo lo demás.

**Regla de negocio** — Una condición que **el negocio exige**. *Ejemplo: "en un trabajo mayor, quien libera el dron no puede ser quien hizo el trabajo".*

**Repositorio** — El objeto que **guarda y recupera** agregados, ocultando cómo y dónde se guardan.

**Shell** — La **cáscara** de la aplicación web: carga los microfrontends según el rol del usuario.

**Simulador** — Un "doble" que **responde en lugar de un servicio no construido**, para que el producto corra completo.

**SOLID** — Cinco principios de buen diseño: responsabilidad única, abierto/cerrado, sustitución de Liskov, segregación de interfaces e inversión de dependencias.

**Specification (especificación)** — Una regla de negocio **pequeña y combinable** con otras (Y, O, NO).

**State (patrón)** — Un objeto que **se comporta según su etapa** y solo permite ciertos pasos.

**Suscriptor** — Quien **recibe** los eventos de un tópico.

**Tópico** — El "canal" o tema de un evento, con nombre y versión. *Ejemplo: `plan-de-mantenimiento.parada-programada.v1`.*

**Trazabilidad** — La capacidad de seguir un elemento **desde el diseño hasta el código** y al revés.

**TUI** — Interfaz de **texto en la terminal**: la pantalla de ArchiForge (`python -m forge studio`).

**Value Object (objeto de valor, VO)** — Un objeto definido **solo por su valor**, inmutable. *Ejemplo: un vuelo de prueba de 7 minutos.*

**Web Component** — Un **elemento HTML propio** y reutilizable que funciona sin depender de un framework concreto.

---
Siguiente: [11 · Decisiones por servicio](11-decisiones-por-servicio.md) · Volver al [índice del manual](README.md).
