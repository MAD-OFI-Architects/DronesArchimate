# 09 · Preguntas frecuentes (y cómo responderlas con honestidad)

Las preguntas están ordenadas como suelen aparecer en una exposición: primero las generales y después las técnicas más incómodas.
Cada respuesta es corta, y remite al documento donde está el detalle.

---

## Sobre el proyecto

### 1. ¿Qué problema resuelve?
La empresa tiene 12 drones de fumigación y necesita mantenerlos **disponibles, seguros y dentro de la norma**. El proyecto toma el diseño del negocio (hecho en ArchiMate) y **construye
automáticamente** los servicios de software que lo implementan: órdenes de trabajo del taller y control de repuestos, con sus pantallas. *(Doc 01.)*

### 2. ¿Qué se construyó, exactamente?
Dos cosas: **ArchiForge** (el programa que lee el diseño y construye software) y **el producto** (dos servicios funcionando + mensajería + pantallas + datos de demostración).
De los **9 contextos** del modelo, **2 están construidos de verdad** y los otros 7 se **simulan**, pero pueden construirse con el mismo procedimiento. *(Docs 01 y 05.)*

### 3. ¿Por qué ArchiMate?
Porque relaciona **estrategia, negocio y sistemas** en un solo modelo estándar, y guarda las **relaciones** (no solo cajas), lo que permite **derivar el código** y rastrearlo hasta el diseño. *(Docs 02 y 06.)*

### 4. ¿La inteligencia artificial hace todo? ¿Qué garantiza que lo que escribe sea correcto?
No. La IA escribe **dentro de un marco estricto**: recibe órdenes de trabajo precisas y, **después de cada etapa, pasan compuertas automáticas** (conformidad con el modelo, arquitectura,
SOLID, patrones, pruebas, humo en contenedores). Si algo no cumple, **se devuelve con el motivo exacto**. Además, las partes deterministas (leer el modelo, generar el compose, etc.) las hace el programa **sin IA**.
*(Doc 03.)*

### 4b. ¿Dónde están las razones de cada decisión?
En `archiforge/decisiones/<servicio>.toml` (texto completo) y resumidas, con la alternativa descartada y el costo aceptado, en el **doc 11**.

### 5. ¿Qué hace el arquitecto y qué hace la herramienta?
El **arquitecto decide** (lenguaje, base de datos, estilo, patrones, canal de eventos, gateway, frontend, despliegue…) y **la herramienta ejecuta fiel a esas decisiones**.
La herramienta **no recomienda ni preselecciona**: si falta una decisión, se detiene y lista las opciones. *(Docs 03 y 04.)*

---

## Sobre el modelo ArchiMate

### 6. ¿Cómo debe estar el modelo para que el programa lo entienda?
Con **etiquetas concretas**: contextos como componentes con la frase «contexto delimitado», agregados con `Rol = Raíz/Entidad/VO`, comandos y eventos con la propiedad `Agregado`,
relaciones de disparo para las políticas, y tablas de apoyo en texto para contratos y relaciones entre contextos. *(Doc 02.)*

### 7. ¿Funciona con cualquier ArchiMate?
**Casi.** Funciona con cualquier modelo que siga esas convenciones, pero hay **una tabla fija** que une los servicios de nivel 3 con sus contextos y pertenece a este modelo. Para otro modelo hay que ampliarla.
Es el pendiente principal para ser 100 % independiente del modelo. *(Docs 02 y 08.)*

### 8. ¿Qué pasa si cambia el modelo?
El programa guarda una **huella** del modelo y de las decisiones. Al volver a construir, **detecta el cambio y reconstruye solo lo afectado**; si no cambió nada, no gasta cuota. *(Doc 03.)*

### 9. ¿Cómo agrego un servicio nuevo?
Si ya existe en el modelo (hay 7 contextos simulados): en la pantalla, **Enter** sobre el contexto → decidir → construir (`b`) → ensamblar (`a`). Al ensamblar, deja de simularse y los demás se reapuntan solos.
Si no existe, primero se agrega al modelo. *(Doc 04.)*

### 10. ¿Cómo sé que el código viene del modelo?
Cada elemento del resumen del modelo (IR) conserva su **identificador original**, y el programa genera un documento de **trazabilidad** por servicio (`entrega-v3/docs/<servicio>/trazabilidad.md`)
que enlaza cada clase con el elemento del modelo que la originó, más un informe de **conformidad** (qué porcentaje de lo esperado existe). *(Docs 02 y 03.)*

---

## Sobre la comunicación entre servicios (interoperabilidad)

### 11. ¿Cómo se comunican los servicios?
Casi todo por **eventos asíncronos** a través de **RabbitMQ**: un servicio avisa "ocurrió esto" y los demás reaccionan. Solo las **consultas puntuales** (habilitación de un técnico, envío de un aviso) son
llamadas directas, protegidas por una **capa anticorrupción** con tiempo máximo. *(Doc 05.)*

### 12. ¿Por qué eventos y no llamadas directas?
Porque evitan el **acoplamiento temporal**: si Repuestos está caído, Intervenciones **no falla**; el aviso espera y se entrega al volver. Además un hecho puede interesar a varios servicios sin que el emisor sepa quiénes son.
El **diseño** del negocio ya definía esas relaciones como asíncronas. *(Docs 05 y 06.)*

### 13. ¿Por qué RabbitMQ y no Kafka?
Porque el volumen es **bajo** (12 drones, unas 2.000 h de vuelo al año) y lo que se necesita es **colas durables, reintentos y una cola de mensajes muertos** con poca operación; RabbitMQ lo da de forma nativa.
Kafka brilla con **millones** de eventos y para **releer el historial**; sería una evolución razonable si Indicadores lo necesitara. *(Doc 06, §7.)*

### 14. ¿Por qué no usar un API Gateway para todo?
Porque el gateway y el bus **resuelven problemas distintos**: el gateway recibe **peticiones de usuarios** (norte-sur); el bus mueve **hechos entre servicios** (este-oeste). Un gateway síncrono entre servicios reintroduciría
el acoplamiento temporal. Y el proyecto **sí usa** un gateway (nginx) para la entrada del público; es una **decisión del arquitecto** y puede cambiarse. *(Doc 06, §7.3 y §8.)*

### 15. ¿Qué pasa si RabbitMQ o un servicio se cae?
Los mensajes **esperan**: las colas son durables y los mensajes persistentes. Si el suscriptor no responde, el bus **reintenta con espera**; tras 5 intentos el mensaje pasa a una **cola de mensajes muertos** que se puede revisar y **reprocesar**.
Esto se **probó con RabbitMQ real**, incluido el reinicio del bus a mitad de entrega. *(Docs 05 y 08.)*

### 16. ¿Qué pasa si el mismo mensaje llega dos veces?
Nada: los consumidores son **idempotentes**. Cada servicio recuerda los `eventId` ya procesados (bandeja de entrada) y, además, cada elemento del mensaje se procesa de forma que repetirlo no duplique sus efectos. *(Doc 05, §6.)*

### 17. ¿Cómo evitan perder un evento?
Con el patrón **outbox**: el evento a enviar se **guarda junto con el cambio de negocio** y un despachador lo envía después. En Intervenciones es **realmente transaccional** (misma transacción de MongoDB).
En Repuestos es **durable pero no transaccional**: si el proceso muere justo entre los dos pasos, ese evento podría perderse. Es un **límite conocido** y el generador ya trae el esqueleto para resolverlo. *(Docs 05 y 08.)*

### 18. ¿Cómo mantienen la consistencia entre dos servicios con bases distintas?
Con **consistencia eventual**: cada servicio cambia **su** dato en **su** transacción y el otro se actualiza al recibir el evento (por ejemplo, el stock se descuenta unos instantes después de cerrar la orden). No hay transacciones distribuidas.
Es el costo de la autonomía, y el negocio lo tolera. *(Docs 05 y 06.)*

### 19. ¿Por qué no usaron Saga?
Una **Saga** coordina operaciones largas que cruzan servicios con compensaciones. Aquí cada operación vive **dentro de un servicio** y el resto se resuelve con eventos simples, así que una transacción local alcanza. Tiene **costo alto** y no resolvería un problema que hoy no existe. *(Doc 07, §6.)*

---

## Sobre las decisiones técnicas

### 20. ¿Por qué dos lenguajes (C# y Python) y dos bases de datos (MongoDB y PostgreSQL)?
Porque cada uno se ajusta a su problema y además **demuestra** que el modelo es independiente de la tecnología:
la **orden de trabajo** es un agregado grande con reglas ricas (C# tipado, documento en MongoDB); las **existencias** exigen consistencia estricta (Python ágil, PostgreSQL relacional).
El costo: el equipo debe dominar dos ecosistemas. *(Doc 06, §4 y §6.)*

### 21. ¿Por qué microfrontends si son solo dos servicios?
Honestamente: con dos servicios y un equipo, una **SPA única** probablemente bastaría. Se eligió microfrontends para **demostrar la arquitectura por dominios** (cada servicio es dueño de su pantalla y se despliega por separado).
Además, hoy hay un formulario **por comando**; en un producto real convendría reorganizar la interfaz **por tareas** del usuario. *(Doc 06, §10.)*

### 22. ¿Por qué Docker Compose y no Kubernetes?
Compose permite **ejecutar todo el producto con un comando** en cualquier máquina, ideal para demostración y desarrollo. Kubernetes es el paso natural para producción con alta disponibilidad, pero
exige un clúster y **no hay un generador que lo respalde**, por eso no se ofrece como opción (sí existe la opción `propio`, que no genera artefactos de despliegue). *(Doc 06, §9.)*

### 23. ¿Qué patrones usaron y por qué esos?
**10 patrones elegidos**: CQRS, Pipeline, Memento, State, Specification, Outbox, Eventos con consumidores idempotentes, ACL, Caché y Cifrado. Cada uno resuelve un problema **que existe** en este negocio
(reglas complejas, ciclo de vida de la orden, no perder eventos, proteger datos personales…). *(Doc 07.)*

### 24. ¿Y por qué no los otros patrones?
Un patrón se usa **cuando el problema existe**; si no, solo suma complejidad. Por ejemplo: no *Saga* ni *Event Sourcing* (costo alto sin necesidad), no *Strategy* (no hay familias de algoritmos), no *Singleton*
(la inyección de dependencias lo hace mejor). La lista completa con el motivo de cada uno está en el doc 07, §6.

### 25. ¿Cumplen los principios SOLID? ¿Cómo lo comprueban?
Una compuerta busca **señales objetivas** (clases que crecen sin límite, cadenas de `if` por tipo, herencias que lanzan "no soportado", puertos con demasiados métodos, instanciación directa de lo concreto) y una **revisión independiente**
aporta el criterio humano. Son **heurísticas**: detectan olores graves, no prueban el principio. La revisión de código encontró dos clases cerca del límite de responsabilidades. *(Docs 03, 07 y 08.)*

### 26. ¿Cómo protegen los datos personales?
Con **cifrado en reposo** (AES-256-GCM) de los datos de personas, con la clave por variable de entorno; si falta la clave, **el servicio no arranca**. Se corrigió un caso en el que Python usaba una clave pública por defecto.
Límites: clave de desarrollo en el compose, sin rotación. *(Docs 06 y 08.)*

---

## Sobre lo que falta (preguntas incómodas)

### 27. ¿Está terminado?
El producto cumple su propósito (dos servicios reales, interoperando, con pantallas y pruebas), pero **tiene límites que conocemos y que están documentados**: autenticación, outbox transaccional en Python, validación de esquemas del bus, etc. *(Doc 08, §4.)*

### 28. ¿Encontraron errores? ¿Qué hicieron?
Sí, y es una fortaleza mostrarlo: una **revisión de código profunda** encontró 11 desviaciones (más un hallazgo que se **retractó** por ser un error de la propia revisión). Entre ellas, la **duplicación de órdenes bajo concurrencia**, que solo apareció probando con el sistema real.
Todas se **corrigieron con pruebas** o se documentaron como límites. *(Doc 08, §2 y §3.)*

### 29. ¿Es seguro? ¿Escala?
**Seguridad:** hoy no hay autenticación en el borde ni entre servicios (ya existe el contexto "Identidad y permisos" en el modelo, sin construir); el control por rol es solo de interfaz.
**Escala:** los servicios no guardan estado local (el estilo microservicio lo exige), así que se pueden replicar; pero Compose es de un solo servidor y la caché es por instancia. Para producción habría que sumar un orquestador y autenticación. *(Doc 08, §4.)*

### 30. ¿Cuánto cuesta construir un servicio?
Las etapas deterministas son gratis; las etapas con agente **consumen cuota** del proveedor de IA (varias sesiones por servicio, con reintentos). Por eso el programa **guarda el avance** y **no repite** lo que ya pasó las compuertas.

### 31. ¿Por qué hay simuladores?
Para que el producto **corra completo** aunque solo dos de los nueve contextos estén construidos, y para **probar la integración** con los que existen en el modelo. Cuando se construye uno real, **los demás no cambian**. Es una decisión del arquitecto (`generar` o `ninguno`). *(Doc 05.)*

### 32. ¿Qué se puede mostrar funcionando en vivo?
La demostración guiada del doc 04: levantar todo con un comando, cargar los datos, ver el stock de `BOM-12` en **3 unidades** porque se cerró la orden de **ADV-06** (**interoperabilidad**), la orden de **ADV-02** *En espera* por falta de repuesto, y la consola de RabbitMQ con las colas.

---
Anterior: [08 · Calidad y pruebas](08-calidad-y-pruebas.md) · Siguiente: [10 · Glosario](10-glosario.md)
