# 06 · Por qué se eligió cada tecnología (y por qué no otras)

> **Alcance de las razones.** Lo que el equipo dejó por escrito (en las decisiones y en el diseño) se cita como tal; el resto de los argumentos es el **análisis técnico** que respalda cada
> elección, para que puedas defenderla. Si la defensa requiere el motivo *histórico* de una decisión, conviene confirmarlo con quien la tomó.

> **Cómo leer este documento.** Cada sección sigue el mismo esquema: **qué se eligió → por qué → qué otras opciones había y por qué no →
> qué costo o límite tiene**. Decir los límites no debilita la decisión: **la hace creíble**.

## 0. Antes de elegir: los criterios

Ninguna tecnología es "la mejor"; es mejor **para algo**. Estos son los criterios que guiaron las decisiones, tomados del propio negocio:

| Criterio | Por qué importa en este negocio |
|---|---|
| **Corrección de las reglas** | Una orden mal liberada es un dron que vuela sin revisión: las reglas del taller deben cumplirse siempre |
| **Disponibilidad parcial** | En campo la conectividad es irregular; una pieza caída no debe tumbar a las demás |
| **Trazabilidad** | La autoridad aeronáutica pide evidencia: todo cambio debe poder reconstruirse |
| **Datos personales** | Hay datos de técnicos: la Ley 1581 de 2012 exige protegerlos |
| **Equipo pequeño** | 17 personas en la empresa: la tecnología debe ser operable sin un equipo de plataforma |
| **Evolución** | El negocio cambiará: hay que poder cambiar una pieza sin reescribir todo |
| **Demostrabilidad** | El proyecto debe mostrar que el mismo modelo se puede construir con tecnologías distintas |

## 1. Quién decidió qué

Para no atribuir a una persona lo que decidió la herramienta (ni al revés):

| Decisión | La decide… | Dónde queda escrito |
|---|---|---|
| Qué hace el negocio (agregados, comandos, eventos, reglas) | El **modelo ArchiMate** (el equipo) | `diseno/` |
| Que las relaciones entre contextos sean asíncronas | El **diseño** (mapa de contextos, Fase 5) | `diseno/Fase05/01_mapa_de_contextos.md` |
| Lenguaje, arquitectura interna, estilo, base de datos, patrones de **cada servicio** | El **arquitecto** | `archiforge/decisiones/<servicio>.toml` |
| Canal de eventos, gateway, frontend, despliegue, simuladores, imágenes | El **arquitecto** | `archiforge/decisiones/plataforma.toml` |
| Las compuertas, el formato de las órdenes de trabajo, el contrato del sobre del bus | La **herramienta** | `archiforge/forge/` |

> **Dónde están las justificaciones registradas.** Las de cada servicio (lenguaje, arquitectura, estilo, base de datos y cada patrón) están en `decisiones/<servicio>.toml` y se resumen en el
> [documento 11](11-decisiones-por-servicio.md). Este documento las amplía con las alternativas y los límites de cada tecnología.

---

## 2. Modelar el negocio con ArchiMate + DDD

**Elegido:** ArchiMate (con la herramienta Archi) para el modelo y *Domain-Driven Design* (DDD, "diseño guiado por el dominio") para organizarlo.

**Por qué**
- ArchiMate conecta **estrategia → negocio → aplicación** en un solo modelo: se puede seguir una capacidad del negocio hasta la clase que la implementa.
- Es un **estándar** (The Open Group): cualquiera que lo conozca puede leerlo.
- Guarda **relaciones**, no solo cajas: eso permite *derivar* el código en lugar de copiarlo a mano.
- DDD da el vocabulario para partir el sistema en **contextos delimitados**, agregados, comandos y eventos: justo lo que el programa necesita leer.

**Alternativas**
| Alternativa | Por qué no |
|---|---|
| UML | Excelente para diseño de clases, pero no relaciona estrategia, procesos y sistemas en un mismo modelo |
| Modelo C4 | Muy claro para comunicar arquitectura de software, pero describe estructura, no el negocio ni sus reglas |
| Solo *Event Storming* (post-its) | Útil para descubrir; no es un artefacto que un programa pueda leer ni versionar |
| Documentos de texto | Se desactualizan y no se pueden recorrer automáticamente |

**Costo:** construir el modelo lleva trabajo (aquí, seis fases) y exige respetar convenciones de etiquetado (ver doc 02).

---

## 3. Un sistema partido en contextos y servicios

**Elegido:** un servicio por **contexto delimitado**, **estilo microservicio** en los dos construidos.

**Por qué**
- El diseño (Fases 3 a 5) separó el negocio en 9 contextos con lenguaje propio y dueños distintos. Cada servicio refleja **un** contexto.
- **Cada servicio tiene su base de datos**: nadie modifica datos ajenos; cambiar la estructura de uno no rompe a otro.
- Un servicio caído no tumba a los demás (importante con conectividad irregular).
- Permite usar **tecnologías distintas** por servicio (ver sección 4).

**Alternativas**
| Alternativa | Por qué no (aquí) | Cuándo sí |
|---|---|---|
| **Monolito** (una sola aplicación) | Más simple de operar, pero mezcla los contextos y no demostraría independencia de tecnología | Equipo muy pequeño, un solo contexto, sin necesidad de escalar partes por separado |
| **Monolito modular** | Buen término medio; la herramienta lo soporta, pero no mostraba la comunicación entre servicios | Un único despliegue con límites internos claros |
| **SOA con orquestador** | Pensado para coordinar procesos largos entre servicios; el proceso aquí se resuelve con eventos | Flujos de negocio largos con muchos pasos coordinados |

**Costo:** más piezas que operar (contenedores, mensajería, trazabilidad entre servicios) y **consistencia eventual** (el stock se descuenta unos instantes
después de cerrar la orden, no en la misma operación).

---

## 4. Lenguajes: C# para Intervenciones, Python para Repuestos

**Elegido:** C# (.NET 8, ASP.NET Core) y Python (FastAPI). Java también está soportado por el generador, pero no se usó en estos dos servicios.

**Por qué dos lenguajes distintos**
- Es una **decisión deliberada**: el modelo es independiente de la tecnología, y construir dos servicios con lenguajes diferentes lo demuestra.
- Además se ajusta a cada problema:

| Servicio | Lenguaje | Razón técnica |
|---|---|---|
| **Intervenciones** | **C#** | Tipado fuerte y excelente soporte de DDD: la orden de trabajo tiene reglas ricas (ciclo de vida, firmas, especificaciones combinables); el compilador atrapa errores antes de correr; ecosistema maduro para transacciones y pruebas |
| **Repuestos** | **Python** | Dominio más acotado (existencias, reservas, reposición); itera rápido; FastAPI da una API clara y validación con poco código |

**Alternativas**
| Alternativa | Por qué no |
|---|---|
| Java / Spring Boot | Igual de válido que C# (el generador lo soporta). Los dos servicios ya cubren un lenguaje tipado de plataforma (C#) y uno dinámico (Python), así que Java no aportaba un contraste nuevo |
| Node.js / TypeScript en el servidor | Válido, pero el frontend ya usa TypeScript; se prefirió variar para demostrar independencia |
| Go | Excelente para servicios de red, pero el modelo y las plantillas del proyecto no lo contemplan |

**Costo:** el equipo debe dominar **dos** ecosistemas; si hay poca gente, esa puede ser una razón para unificar el lenguaje en un proyecto real.

---

## 5. Arquitectura interna: Clean + DDD (Intervenciones) y Hexagonal (Repuestos)

**Elegido:** *Clean Architecture con DDD* en Intervenciones y *Arquitectura Hexagonal* en Repuestos.

Las dos comparten la misma idea (**el núcleo del negocio no depende de la tecnología**); difieren sobre todo en cómo se organizan:

| | Clean + DDD | Hexagonal (puertos y adaptadores) |
|---|---|---|
| Organización | Capas concéntricas: Dominio → Aplicación → Infraestructura/API | Un núcleo rodeado de puertos (interfaces) y adaptadores |
| Fuerte en | Dominios con **muchas reglas** y un ciclo de vida complejo | Servicios con **muchas conexiones** externas (bus, base, avisos) |
| Por qué aquí | La orden de trabajo concentra reglas (liberar, vuelo de prueba, serie, cierre) | Repuestos conversa con inventario, bus y avisos: cada uno es un puerto claro |

**Alternativas:** arquitectura en capas clásica (la base de datos "manda" y el dominio la conoce) o transacción por tabla (*transaction script*).
No se eligieron porque acoplan las reglas del negocio a la tecnología y dificultan probarlas aisladas.

**Costo:** más clases e interfaces. Para un CRUD simple sería exagerado; aquí se justifica por la riqueza de reglas.
*(Honestidad: la diferencia práctica entre ambas arquitecturas es de organización más que de capacidad; la elección también cumple el propósito de mostrar las dos.)*

---

## 6. Bases de datos: MongoDB (Intervenciones) y PostgreSQL (Repuestos)

**Elegido:** una base **por servicio**, de tipo distinto.

| Servicio | Base | Razón |
|---|---|---|
| **Intervenciones** | **MongoDB** (con conjunto de réplicas) | La orden de trabajo es un **agregado**: una orden con sus tareas, consumos, hallazgos, vuelos y firmas que se leen y se guardan **juntos**. Un **documento** lo representa tal cual (patrón *Memento*), sin dividirlo en seis tablas. El conjunto de réplicas permite **transacciones**, necesarias para guardar la orden y su mensaje de salida a la vez |
| **Repuestos** | **PostgreSQL** | Las existencias exigen **consistencia estricta** (no vender dos veces la misma unidad), claves únicas y transacciones; el modelo es naturalmente tabular |

**Alternativas**
| Alternativa | Por qué no |
|---|---|
| Una sola base compartida | Rompe la autonomía: un cambio en una tabla afecta a ambos servicios |
| PostgreSQL también en Intervenciones | Posible (con columnas JSON o tablas relacionadas); se prefirió el documento por la forma del agregado |
| MongoDB también en Repuestos | El stock se beneficia de restricciones y transacciones relacionales; sería un ajuste peor |
| Bases en memoria (Redis, etc.) | Rápidas pero no son la fuente de verdad que se necesita para evidencia |
| Event Sourcing (guardar solo eventos) | Potente para auditoría total, pero añade complejidad (versionado de eventos, proyecciones); aquí un historial simple alcanza |

**Costo:** hay **dos** bases que operar. El conjunto de réplicas de MongoDB se configura automáticamente en el compose, pero en producción requiere cuidado.

---

## 7. Mensajería: RabbitMQ

Es la decisión que más se pregunta, así que va con más detalle.

**Elegido:** eventos asíncronos entre servicios, transportados por **RabbitMQ**, a través de un pequeño servicio puente (`event-bus`) que conserva el contrato HTTP.

### 7.1 Por qué eventos (y no llamadas directas)

El mapa de contextos del **diseño** definió estas relaciones como **asíncronas**. Y tiene sentido de negocio:

- **Acoplamiento temporal:** con llamadas directas, para abrir una orden *Plan* tendría que esperar a que *Intervenciones* y *Repuestos* estén arriba **en ese instante**.
  Con eventos, Plan avisa y **sigue**; cada uno reacciona cuando puede.
- **Un hecho, varios interesados:** "se programó una parada" interesa a dos servicios (y mañana a más) sin que el emisor sepa quiénes son.
- **Resiliencia:** un servicio caído **no pierde** el aviso; lo recibe al volver.
- **Se evita la transacción distribuida:** cada servicio cambia **su** dato en **su** transacción; la coordinación ocurre por eventos.

### 7.2 Por qué RabbitMQ (y no otras opciones)

| Opción | Qué ofrece | Por qué sí / no aquí |
|---|---|---|
| **RabbitMQ** ✅ | Colas durables, **enrutamiento por tópico**, reintentos con espera, **cola de mensajes muertos** nativa, consola de administración | Encaja con lo que se necesita (entregar un mensaje a cada suscriptor, reintentar, apartar lo que falla). Poca operación. Volumen bajo |
| **Apache Kafka** | Registro distribuido de eventos: altísimo volumen, **orden por clave**, se pueden **releer** eventos pasados | Es la herramienta correcta para **millones** de eventos y análisis sobre el historial. Aquí el volumen es bajo (12 drones, unas 2.000 h de vuelo al año), y Kafka añade mucha más operación. **Es una evolución razonable** si Indicadores necesitara reprocesar historia |
| **API Gateway síncrono / llamadas REST** | Simple, directo | Reintroduce el acoplamiento temporal: si un servicio cae, la operación falla. Sirve para **consultas**, no para propagar hechos |
| **Servicios en la nube** (Azure Service Bus, Amazon SQS/SNS, etc.) | Gestionados, sin servidores propios | Muy buena opción en producción; se evitó para que el producto **corra completo en una laptop** sin cuentas de nube |
| **Base de datos compartida** | Cero infraestructura | Rompe la autonomía de cada servicio: es justo lo que se quiere evitar |
| **Intercambio por archivos** | Es lo que el diseño usa con sistemas **externos** (D-18) | Para sistemas externos sin API es correcto; entre servicios propios sería lento e innecesario |

### 7.3 Una aclaración clave: gateway **no** es lo mismo que bus

Se suele preguntar "¿por qué no resolver todo con un API Gateway?". Son cosas **distintas** que se complementan:

```
   API GATEWAY                                   BUS DE EVENTOS
   (norte ⇄ sur)                                 (este ⇄ oeste)

   Navegador ──► gateway ──► servicios           Servicio A ──► bus ──► Servicio B

   Resuelve: ¿por dónde entra el público?        Resuelve: ¿cómo se avisan los servicios entre sí?
   Un solo punto de entrada y de seguridad       Sin conocerse, sin esperarse
```

El gateway **no** sustituye al bus: el primero mueve **peticiones de usuarios**; el segundo mueve **hechos entre servicios**.

### 7.4 La historia honesta del bus (útil para la exposición)

1. El generador **empezó** con un "bus" mínimo de unas 60 líneas que repartía mensajes **en memoria** y los descartaba tras 5 intentos fallidos. Su propio comentario decía que
   "hace el papel de RabbitMQ": era un **sustituto de demostración**.
2. Una revisión del código lo detectó como el punto débil: si el bus se reiniciaba, los mensajes en vuelo **se perdían**.
3. Se reemplazó por **RabbitMQ**, **sin tocar los servicios** (porque el contrato HTTP se mantuvo): ahora los mensajes sobreviven a reinicios, se reintentan y los
   agotados quedan en una cola de mensajes muertos revisable.
4. La elección del canal pasó a ser **una decisión del arquitecto** (`rabbitmq` o `memoria`), no algo fijo del generador.

Esto demuestra algo valioso: la **arquitectura permitió cambiar la infraestructura** sin reescribir el negocio.

### 7.5 Formato de los mensajes

**JSON versionado** (`...v1`) con un sobre común. Alternativas como **Avro o Protobuf con registro de esquemas** son más compactas y estrictas, pero exigen más
infraestructura; con pocos contratos y legibilidad como prioridad, JSON es suficiente. *Límite conocido:* hoy el bus **no valida** el contenido contra el contrato
(solo exige `topic` y `eventId`).

---

## 8. API Gateway: nginx

**Elegido (por decisión del arquitecto):** **nginx** como único punto de entrada: sirve las pantallas y enruta `/api/<servicio>/`.

**Por qué:** es ligero, estable, de configuración simple (un archivo) y suficiente para enrutar por prefijo y servir archivos estáticos.

**Alternativas:** Kong, Traefik o el gateway de un proveedor de nube (añaden autenticación, límites de uso, panel de administración); se justifican cuando hay
muchos servicios y políticas de seguridad en el borde. **La herramienta lo permite**: con la opción `propio` no genera gateway y documenta las rutas que el equipo debe configurar.

**Límite:** nginx **no** valida identidad aquí; el control por rol de las pantallas ocurre en el cliente. Un despliegue real debería sumar autenticación en el borde.

---

## 9. Contenedores y despliegue: Docker Compose

**Elegido (por decisión del arquitecto):** **Docker** para empaquetar cada pieza y **Compose** para levantarlas juntas con un solo comando.

**Por qué:** cualquiera puede ejecutar el producto completo en su máquina con `docker compose up`; es reproducible y lo suficientemente simple para una demostración y desarrollo.

**Alternativas**
| Alternativa | Por qué no ahora |
|---|---|
| **Kubernetes** | Es el estándar para producción con muchas réplicas y autoescalado, pero exige un clúster y conocimiento específico. **No se ofrece como opción** porque no hay generador que lo respalde ni forma de verificarlo aquí |
| Instalar todo directamente en el servidor | Poco reproducible: "en mi máquina funciona" |
| Servicios gestionados de la nube | Excelente en producción; fuera del alcance de una demostración local |

**Costo/límite:** Compose es para un solo servidor. Para producción con alta disponibilidad habría que pasar a un orquestador (y la opción `propio` existe para eso).

---

## 10. Frontend: microfrontends con Web Components (React + Vite + TypeScript)

**Elegido (por decisión del arquitecto):** **un remote por servicio**, empaquetado como **Web Component**, cargado por un **shell** que filtra por rol.

**Por qué**
- Cada microfrontend es **dueño** de la interfaz de su servicio y se construye y despliega por separado.
- Un **Web Component** es un elemento HTML estándar: el shell lo carga sin depender del framework con el que se hizo.
- **React + Vite + TypeScript** dan una base moderna, rápida de construir y con tipos.
- El **sistema de diseño** compartido (variables de color y espaciado) mantiene la apariencia unificada.

**Alternativas**
| Alternativa | Por qué no (o cuándo sí) |
|---|---|
| **SPA única** (una sola aplicación web) | **Más simple** y, con dos servicios y un solo equipo, probablemente **suficiente**. Los microfrontends pagan cuando equipos distintos publican a ritmos distintos. Se eligió microfrontends por el objetivo de demostrar la arquitectura por dominios |
| **Angular** | Válido y completo; no hay generador que lo respalde hoy (por eso no se ofrece como opción) |
| **Module Federation** (de Webpack) | Potente pero acopla a una herramienta de empaquetado concreta; los Web Components son más neutrales |
| **Páginas del servidor** (renderizado en el backend) | Menos interactivo y mezcla interfaz con servicio |

**Costo honesto:** con **solo dos** servicios, la partición en microfrontends es más una **demostración** que una necesidad. Y un formulario **por comando** refleja el modelo, pero un usuario real
trabajaría por **tareas** (una pantalla de orden con acciones contextuales). Es una mejora de experiencia de usuario, no un defecto de arquitectura.

---

## 11. Cifrado de datos personales: AES-256-GCM

**Elegido (por decisión del arquitecto):** **AES-GCM** con clave por variable de entorno.

**Por qué:** AES-GCM es un estándar, **cifra y autentica a la vez** (si alguien altera el dato, se detecta), está en las bibliotecas estándar de .NET y Python, y cubre la protección
de datos personales exigida por la **Ley 1581 de 2012**.

**Alternativas:** *ChaCha20-Poly1305* (equivalente en seguridad, más rápido en equipos sin aceleración AES; **también disponible como opción** en el generador); cifrar solo a nivel de disco o de base
de datos (protege contra robo de disco, no contra quien accede a la base); un servicio de gestión de claves (*KMS*) de la nube.

**Límites a conocer**
- En Intervenciones el *nonce* se deriva del texto (cifrado **determinista**): así el documento no cambia si el dato no cambia, a costa de que dos textos iguales produzcan el mismo cifrado.
- No hay **rotación de claves** ni identificador de clave en el texto cifrado.
- La clave del compose es **de desarrollo**; en producción debe venir de un gestor de secretos.
- Si falta la clave, **el servicio no arranca** (se corrigió un caso en el que Python usaba una clave pública por defecto).

---

## 12. Formato de errores: Problem Details (RFC 9457)

**Elegido:** ambos servicios responden errores con el estándar **Problem Details** (`application/problem+json`), con un campo `regla` y un `codigo` del contrato.
**Por qué:** es un estándar, lo entienden las herramientas de API, y unifica el comportamiento entre dos servicios en lenguajes distintos.
**Alternativa:** un formato propio por servicio (más rápido al principio, pero cada cliente tendría que aprender dos).

---

## 13. Pruebas

| Capa | Herramienta | Qué se prueba |
|---|---|---|
| Servicios C# | **xUnit** + servidor de pruebas | Reglas del dominio, comandos, rutas HTTP completas con adaptadores en memoria |
| Servicios Python | **pytest** | Dominio, aplicación, adaptadores (incluida una base SQL real sobre SQLite) y rutas |
| Pantallas | **Vitest** + Testing Library | Cada formulario: valida, envía el cuerpo correcto, muestra la regla en lenguaje claro |
| El programa | **pytest** | Lector, manifiesto, compuertas, TUI, decisiones (pruebas herméticas: sin agente ni Docker) |
| El conjunto | **Docker** + pruebas reales | Mensajería con fallos, concurrencia (ver doc 08) |

**Por qué:** cada capa se prueba con la herramienta **estándar de su lenguaje**, de modo que cualquier persona del ecosistema puede mantenerlas.

---

## 14. Generación con IA dentro de compuertas

**Elegido:** que un **agente de IA** escriba el código, **sujeto a compuertas automáticas** y con las decisiones del arquitecto como ley.

| Alternativa | Fortaleza | Por qué no sola |
|---|---|---|
| **Plantillas fijas** (generadores clásicos) | Resultado idéntico y predecible | Rígidas: no pueden escribir las reglas propias de cada dominio |
| **IA libre** (pedirle "hazme el sistema") | Rápida | Sin garantías: puede inventar requisitos, ignorar el diseño o dejar piezas sueltas |
| **Escribir todo a mano** | Control total | Lento, y el código se aleja del modelo con el tiempo |
| **IA + compuertas** ✅ | Flexibilidad de la IA **más** verificación objetiva | Costo: usa cuota del agente y las compuertas son heurísticas (no prueban, detectan señales) |

Las partes **deterministas** (leer el modelo, derivar el manifiesto, generar bus/compose/esqueletos) las hace el programa **sin IA**, para que siempre den el mismo resultado.

---

## 15. Simuladores de los contextos no construidos

**Elegido (por decisión del arquitecto):** generar **simuladores** para que el producto corra completo aunque solo dos servicios sean reales.
**Por qué:** permite ver el flujo de extremo a extremo y probar la integración con los contextos que existen en el modelo pero aún no se construyen.
**Alternativa:** dejar sin responder lo que no se construyó (el producto no podría demostrarse) o usar *mocks* dentro de cada prueba (no sirven para una demostración integrada).
**Garantía:** si se construye el servicio real, **los demás no cambian**: leen la URL de su proveedor de una variable de entorno.

---

## Resumen en una tabla (para proyectar)

| Tema | Elegido | Principal alternativa | Razón decisiva |
|---|---|---|---|
| Modelo | ArchiMate + DDD | UML / C4 | Conecta negocio y código y es leíble por programa |
| Partición | Servicios por contexto | Monolito | Autonomía de datos y de fallos |
| Lenguajes | C# y Python | Java / Node | Contraste deliberado + ajuste a cada dominio |
| Arquitectura interna | Clean+DDD y Hexagonal | Capas clásicas | El negocio no depende de la tecnología |
| Bases | MongoDB y PostgreSQL | Una sola compartida | Forma del dato + autonomía |
| Mensajería | RabbitMQ | Kafka / REST | Colas durables, reintentos y cola de mensajes muertos con poca operación |
| Gateway | nginx | Kong / Traefik | Simple y suficiente (cambiable) |
| Despliegue | Docker Compose | Kubernetes | Reproducible en una laptop |
| Frontend | Microfrontends (Web Components) | SPA / Angular | Propiedad por servicio y neutralidad de framework |
| Cifrado | AES-256-GCM | ChaCha20 / KMS | Estándar, autenticado y ya disponible |
| Errores | Problem Details | Formato propio | Estándar y uniforme |
| Construcción | IA + compuertas | Plantillas / IA libre | Flexibilidad con verificación |

---
Anterior: [05 · El producto generado](05-el-producto-generado.md) · Siguiente: [07 · Justificación de patrones](07-justificacion-de-patrones.md)
