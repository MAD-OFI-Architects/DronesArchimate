---
tags: [proyecto, entrevista, fase-0, drones, preguntas]
aliases: [Banco de preguntas Drones, Guion de entrevista Drones]
---

# Banco de preguntas de entrevista — Mantenimiento preventivo de drones de fumigación (Fase 0)

Guion de entrevista organizado en 16 bloques temáticos, con verificación de consistencia (sección 17), preguntas de diseño que no deben hacerse (sección 18), plantilla de registro de hallazgos (sección 19) y checklist de cobertura (sección 20).

> [!info] Cómo leer este documento
> - Es una entrevista completa escrita **desde su punto de vista** (el entrevistador). Cada pregunta se puede copiar y pegar.
> - Etiquetas: **[A]** abierta · **[P]** profundización · **[V]** validación · **[N]** pide números/fórmulas · **[C]** caso real/ejemplo.
> - `→ V#` indica qué vista o producto alimenta la respuesta (V1 motivación, V2 capacidades, V3 E2E, V4 servicios/ACL, V5 dominios, V6 agregados, V7 glosario, V8/V9 contextos e interoperabilidad, V11 canvas).

> [!warning] Regla de oro (del enunciado)
> A la IA experta se le pregunta **solo por el negocio**: cómo funciona, quién hace qué, con qué datos, bajo qué reglas y normas. **Nunca** le pidan dominios, agregados, mapa de capacidades, mapa de contextos, servicios ni vistas ArchiMate. Eso lo derivan ustedes. (Más abajo hay una lista de preguntas prohibidas y cómo redirigir.)

---

## 0. Cómo conducir la entrevista

### 0.1 Orden y tiempo recomendado

| Sesión | Bloques | Duración | Objetivo |
|---|---|---|---|
| **S1** | 1 Contexto · 2 Operación de la fumigación · 3 Actores y organización · 10 Capacidades | 45–60 min | Entender el negocio completo (base para V2 y V3) |
| **S2** | 4 Proceso de mantenimiento preventivo · 5 Despiece y condiciones · 6 Repuestos y consumibles · 7 Plan de mantenimiento | 60 min | El corazón del alcance |
| **S3** | 8 Registro de horas, ciclos y telemetría · 9 Indicadores · 11 Excepciones | 45–60 min | Datos y métricas |
| **S4** | 12 Normatividad · 13 Interoperabilidad | 60 min | Normas y fronteras con otros sistemas |
| **S5** | 14 Motivación y estrategia · 15 Alcance · 16 Cierre y validación | 45–60 min | V1, límites del software, confirmar |

Si tienen una sola sesión larga, mantengan este orden: **de lo general a lo específico**, y **normativa e interoperabilidad después de entender el proceso**.

### 0.2 Técnicas que deben usar en TODAS las preguntas

1. **Una pregunta a la vez.** No peguen bloques enteros.
2. **Pidan siempre un ejemplo concreto** ([C]): "Cuéntenos un caso real de la última temporada".
3. **Pidan números y fórmulas** ([N]): umbrales, frecuencias, costos, tiempos, porcentajes.
4. **Los "5 porqués":** ante una regla, pregunten "¿por qué?" hasta llegar a la razón de negocio o normativa.
5. **"¿Y si falla?"** para cada paso: genera las excepciones.
6. **Validen cada bloque** con un resumen de 5–8 líneas: "Entendemos que… ¿es correcto? ¿Qué corregiría?".
7. **Reintroduzcan datos fijos** (flota, personal) al inicio de cada sesión si la IA no recuerda.
8. **Repregunten en otra sesión** 3–4 datos numéricos para detectar contradicciones (anótenlos como "pruebas de consistencia").
9. Pidan que **marque su nivel de certeza** en normas y cifras: "¿Esto es práctica general, norma o su criterio?".
10. Registren cada respuesta importante como **hallazgo H-xx** (plantilla de la sección 19).

### 0.3 Mensaje de apertura de cada sesión (copiar y adaptar)

```text

ROL
Eres Pompilio Ospina, Jefe de Operaciones y Mantenimiento de "AgroDrones del Valle S.A.S.", una empresa colombiana que presta servicios de fumigación de cultivos con una flota de drones. Tienes 12 años de experiencia, los últimos 6 en aviación agrícola no tripulada y mantenimiento de flotas. Hablas como una persona de operación de campo y taller: directo, práctico, con ejemplos reales; no usas jerga de arquitectura de software.

SITUACIÓN
La empresa necesita un software que apoye su mantenimiento preventivo para mantener la flota disponible, segura y dentro de la normatividad aeronáutica. Un equipo de estudiantes de arquitectura de software te entrevistará para entender tu negocio. Tú eres la fuente de conocimiento del NEGOCIO; ellos harán el diseño.

DATOS FIJOS DE LA EMPRESA (mantenlos idénticos en todas las sesiones)
- Flota: [N] drones de [marcas/modelos], con antigüedad entre [X] y [Y] años.
- Operación: [regiones], cultivos de [cultivos], aprox. [N] hectáreas al año, con picos en [temporadas].
- Personal: [N] pilotos, [N] técnicos de mantenimiento, [áreas existentes: operaciones, almacén, administración…].
- Herramientas actuales: [por ejemplo Excel, formatos en papel, plataforma del fabricante]. No inventes otras.
- Clientes: [tipos].
(Si un dato no está aquí y te lo preguntan, invéntalo de forma plausible y realista, y mantenlo desde entonces.)

REGLAS DE COMPORTAMIENTO
1. Responde solo lo que te pregunten, de forma concreta y no demasiado larga. Si la respuesta es larga, ofrece continuar por partes.
2. Da ejemplos reales, cifras plausibles, nombres de documentos, roles y casos. Incluye imperfecciones, atajos y malas prácticas actuales de la empresa, como en la vida real.
3. NO diseñes ni propongas: mapas de capacidades, dominios, agregados, servicios, mapas de contextos, diagramas, modelos de datos ni arquitectura de software. Si te lo piden, responde: "Eso es parte de su diseño; yo puedo explicarles cómo funciona el negocio".
4. Si no sabes algo, dilo ("eso habría que verificarlo con…"). No inventes con falsa seguridad.
5. En temas normativos (Aerocivil, ICA, ambientales, SST, seguros), indica siempre tu nivel de certeza (alto/medio/bajo), distingue entre norma, recomendación del fabricante y práctica interna, y no inventes números de resolución, artículos ni fechas. Sugiere qué documento oficial deberían consultar.
6. Sé consistente con lo dicho antes. Si detectas que te contradices, dilo y corrige.
7. Si una pregunta es ambigua, pide aclaración en una línea.
8. No hagas tú preguntas al equipo salvo para aclarar la suya.
9. Si te piden resumir, resume solo lo conversado y marca claramente lo incierto.

Confirma que entendiste respondiendo solo: "Listo, soy Pompilio. ¿Por dónde empezamos?"


Hola Pompilio Ospina. Somos estudiantes de arquitectura de software y estamos entendiendo el proceso de mantenimiento preventivo de la flota de drones de fumigación de [empresa]. Hoy queremos hablar de [bloques]. Nos interesa cómo funciona el negocio hoy (no cómo debería ser el software). Si no está seguro de algo o es un tema normativo, díganos su nivel de certeza para verificarlo después. ¿Empezamos?


```

---

## 1. Bloque — Contexto de la organización y del negocio → V1, V2

1. **[A]** Cuéntenos a qué se dedica la empresa, cuándo se creó y cómo llegó a prestar fumigación con drones.
2. **[P]** ¿Cuántos drones tiene la flota, de qué marcas y modelos, y de qué antigüedad? ¿Son todos del mismo tipo?
3. **[N]** ¿Cuántas hectáreas fumigan al año, en qué regiones y para qué cultivos? ¿Cuántas horas de vuelo acumula la flota al año?
4. **[P]** ¿Cómo es el calendario del negocio? ¿Hay temporadas pico y valle? ¿Cómo cambia la demanda de mantenimiento entre unas y otras?
5. **[P]** ¿Quiénes son los clientes (grandes agroindustrias, medianos productores, asociaciones) y cómo contratan (por hectárea, por temporada, por jornada)?
6. **[P]** ¿Cómo gana dinero la empresa y cuánto pesa el mantenimiento en los costos? **[N]**
7. **[P]** ¿Cuál es la ventaja competitiva de la empresa frente a otras que fumigan con drones o con avioneta?
8. **[P]** ¿Cuáles son los mayores riesgos del negocio hoy (accidentes, incumplimiento normativo, indisponibilidad de flota, pérdida de cliente)?
9. **[P]** ¿Cómo está organizada la empresa? ¿Cuáles son las áreas y jefaturas? ¿Dónde está ubicado el mantenimiento y de quién depende?
10. **[P]** ¿Con qué herramientas se gestionan hoy las cosas (papel, Excel, algún software, WhatsApp)? ¿Qué funciona bien y qué no?
11. **[V]** Resumir el negocio en 6 líneas y pedir correcciones.

---

## 2. Bloque — Operación de fumigación (el "cliente" del mantenimiento) → V2, V3

> Objetivo: entender de dónde salen las horas y ciclos, y cómo la operación depende de la flota.

1. **[A]** Descríbanos una misión típica de fumigación, desde que se acepta el servicio hasta que el dron vuelve a bodega.
2. **[P]** ¿Quién planea la misión, quién la vuela, quién carga el producto y quién registra el vuelo?
3. **[N]** ¿Cuánto dura un vuelo/una carga de tanque, cuántos vuelos por jornada, cuántos drones por servicio?
4. **[P]** ¿Cómo se asignan los drones a los servicios? ¿Qué criterios usan (disponibilidad, estado, horas acumuladas, tipo de cultivo)?
5. **[P]** ¿Qué se hace antes del vuelo (inspección prevuelo) y después (limpieza, descarga de datos, cambio de batería)? ¿Cuáles de esas tareas son mantenimiento y cuáles operación?
6. **[P]** ¿Qué agroquímicos manejan y cómo afectan al equipo (corrosión, obstrucción de boquillas, residuos)?
7. **[P]** ¿Qué condiciones ambientales (viento, humedad, altura, polvo) aceleran el desgaste?
8. **[C]** Cuéntenos de una vez que un dron no estuvo disponible cuando se necesitaba. ¿Qué pasó con el servicio al cliente?
9. **[V]** Confirmar el flujo de la misión y de dónde salen los datos de operación.

---

## 3. Bloque — Actores, roles y responsabilidades → V3, V4

1. **[A]** ¿Quiénes participan en el mantenimiento preventivo, de forma directa o indirecta?
2. **[P]** Para cada rol: ¿qué hace, qué decide, qué firma, qué registra, ante quién responde?
   - Piloto remoto / operador
   - Técnico de mantenimiento
   - Inspector / responsable de calidad o aeronavegabilidad
   - Jefe de mantenimiento / operaciones
   - Almacenista / compras
   - Coordinador de servicios (programación con clientes)
   - Gerencia / responsable de seguridad operacional
3. **[P]** ¿Qué certificaciones o competencias se exigen a técnicos y pilotos? ¿Quién las valida y cada cuánto vencen? ¿Qué pasa si un técnico no tiene la certificación vigente?
4. **[P]** ¿Quién autoriza **liberar** un dron al servicio después de una intervención? ¿Puede ser la misma persona que ejecutó el trabajo?
5. **[P]** ¿Hay terceros que intervienen (fabricante, talleres externos, distribuidores de repuestos, aseguradora, autoridad)? ¿Qué hacen exactamente?
6. **[P]** ¿Cómo se coordinan hoy entre sí estos roles (reuniones, mensajes, formatos)?
7. **[V]** Confirmar la lista de roles y su responsabilidad en una tabla.

---

## 4. Bloque — Proceso de mantenimiento preventivo (E2E) → V3, V4, V5

1. **[A]** Describanos, paso a paso, cómo funciona hoy el mantenimiento preventivo, desde que un dron opera hasta que queda liberado y registrado.
2. **[P]** ¿Cuáles son las **etapas** y qué dispara el inicio de cada una? ¿Qué eventos marcan el fin de una etapa?
3. **[P]** ¿Cómo se diferencia el mantenimiento **preventivo** del **correctivo** y del **predictivo/por condición** en su empresa? ¿Cuánto de cada uno se hace hoy? **[N]**
4. **[P]** ¿Cómo y cuándo se detecta que un dron o componente "ya le toca"? ¿Quién lo detecta y con qué dato?
5. **[P]** ¿Cómo se programa la intervención? ¿Quién decide la fecha y cómo evita chocar con servicios ya comprometidos con clientes?
6. **[P]** ¿Qué pasa en el momento de la intervención? (diagnóstico, desmontaje, cambio, pruebas, calibración, vuelo de prueba). ¿Qué documentos o formatos se llenan?
7. **[P]** ¿Cómo se verifica que el trabajo quedó bien y quién libera el dron?
8. **[P]** ¿Qué se registra al cerrar la intervención (fecha, horas, componente cambiado, técnico, repuesto usado, costo)?
9. **[P]** ¿Cómo se actualiza el "reloj" de mantenimiento después de una intervención (se reinicia, se arrastra)?
10. **[P]** ¿Qué parte del proceso es más lenta, más costosa o más propensa a error hoy?
11. **[C]** Cuéntenos un caso reciente completo, de principio a fin, con fechas aproximadas.
12. **[V]** Resumir el flujo en pasos numerados y pedir corrección.

---

## 5. Bloque — Despiece y condiciones de mantenimiento → V5, V6, V7

> Es el alcance más técnico: lo que se modela como "dron", "componente" y "condición". **Pidan siempre ejemplos concretos por componente.**

1. **[A]** ¿Cómo se descompone un dron agrícola en subsistemas y componentes? Cuéntenos el despiece completo de uno de sus modelos.
2. **[P]** ¿Cuáles son los subsistemas (propulsión, energía, aspersión, navegación/control, estructura, comunicaciones, sensores) y qué componentes tiene cada uno?
3. **[P]** ¿El despiece es igual para todos los modelos? ¿Cómo manejan diferencias entre marcas o versiones?
4. **[P]** ¿Cada componente tiene número de serie o lote? ¿Se rastrea individualmente?
5. **[P]** ¿Los componentes se **mueven entre drones** (por ejemplo una batería o un motor)? ¿Cómo se registra qué componente está instalado en qué dron y desde cuándo?
6. **[P]** ¿Hay componentes con **vida útil limitada** (se retiran por horas, ciclos o fecha) y otros "a condición" (se cambian si se encuentra desgaste)? Deme ejemplos de cada uno.
7. **[P]** Para cada tipo de componente (motores, hélices, baterías, bombas, boquillas, controlador de vuelo, ESC, GPS/RTK, radar, estructura, mangueras, filtros, tanque):
   - **[N]** ¿Cuál es su condición de mantenimiento: por **horas**, por **ciclos**, por **calendario**, por **estado**?
   - **[N]** ¿Cuál es el intervalo o umbral exacto y de dónde sale (manual del fabricante, norma, experiencia propia)?
   - ¿Qué tarea se hace (inspección, limpieza, calibración, cambio, prueba)?
   - ¿Qué consumibles/repuestos requiere?
8. **[P]** Si un componente tiene **varias condiciones a la vez** (por ejemplo horas y calendario), ¿cuál manda? ¿"lo que ocurra primero"?
9. **[P]** ¿Cómo se definen y cuentan los **ciclos**? ¿Un ciclo es un vuelo, una carga de batería, un llenado de tanque? ¿Es distinto para cada componente?
10. **[P]** ¿Qué tolerancias se permiten (adelantar o diferir una intervención)? ¿Cuánto y quién autoriza?
11. **[P]** ¿Qué pasa si un dron está en servicio cuando se vence una condición? ¿Puede seguir volando? ¿Qué decisiones se toman?
12. **[P]** ¿Cómo se maneja la **vida remanente** de componentes que pasan de un dron a otro o se reparan?
13. **[P]** ¿Qué tareas de mantenimiento se hacen en campo y cuáles en taller/base?
14. **[P]** ¿Cómo se gestionan las actualizaciones de firmware o calibraciones periódicas? ¿Se consideran mantenimiento preventivo?
15. **[C]** Tomemos una batería y una boquilla: describa su ciclo de vida completo, desde que entra a bodega hasta que se retira.
16. **[V]** Armar con el experto una tabla "componente → condición → umbral → tarea → repuestos" para 4–5 componentes y confirmar.

---

## 6. Bloque — Repuestos y consumibles → V4, V6, V9

1. **[A]** ¿Qué repuestos y consumibles necesita el mantenimiento preventivo de la flota?
2. **[P]** Para cada tipo de cambio (batería, hélice, boquilla, filtro, motor…): ¿qué repuestos y cantidades exactas se necesitan? ¿Existen **kits** de mantenimiento?
3. **[P]** ¿Cómo se maneja el stock hoy? ¿Dónde se guarda, quién lo controla y cómo se sabe qué hay?
4. **[N]** ¿Cómo se define el stock mínimo o punto de reposición de los repuestos críticos? ¿Cuál es el tiempo de entrega de los proveedores?
5. **[P]** ¿Quiénes son los proveedores (fabricante, distribuidor local, importación)? ¿Cuánto demora importar? ¿Qué pasa con los trámites aduaneros?
6. **[P]** ¿Cómo se solicita y aprueba una compra de repuestos? ¿Quién autoriza, con qué monto?
7. **[P]** ¿Cómo se trata un repuesto con **garantía** (reclamación al fabricante)? ¿Qué datos se necesitan?
8. **[P]** ¿Qué hacen con los componentes retirados (descarte, reparación, devolución, disposición ambiental)? ¿Cómo se registran?
9. **[P]** ¿Cómo manejan la **trazabilidad** de lote y serie de un repuesto desde que llega hasta que se instala?
10. **[P]** ¿Qué pasa si falta un repuesto cuando se debe hacer la intervención?
11. **[N]** ¿Cuál es el costo aproximado de los componentes más críticos y de los consumibles más frecuentes?
12. **[V]** Confirmar la relación entre tareas, repuestos y proveedores.

---

## 7. Bloque — Plan de mantenimiento y su programación → V3, V4, V6

1. **[A]** ¿Cómo está estructurado el **plan de mantenimiento** de un dron? ¿Es un documento, una hoja de cálculo, un calendario?
2. **[P]** ¿El plan se define por modelo de dron, por componente, o por dron individual? ¿Quién lo define y cómo lo aprueba?
3. **[P]** ¿Cómo se versionan o actualizan los planes (por cambios del fabricante, por hallazgos, por normativa)?
4. **[P]** ¿Cómo se **programan** las intervenciones? ¿Cada cuánto se revisa el estado de la flota para decidir? ¿Quién lo hace?
5. **[P]** ¿Cómo agrupan tareas (varios componentes en una sola parada del dron) para minimizar la indisponibilidad?
6. **[P]** ¿Cómo se concilia el plan con la **programación de servicios a clientes**? ¿Quién tiene prioridad cuando hay conflicto?
7. **[P]** ¿Cómo se asignan técnicos y espacio de trabajo a cada intervención? ¿Qué restricciones hay (certificación, capacidad)?
8. **[P]** ¿Cómo se notifica a los involucrados (pilotos, técnicos, almacén, coordinación)? ¿Con cuánta antelación?
9. **[P]** ¿Qué pasa cuando una intervención programada **no se cumple** (por falta de repuesto, técnico, tiempo)? ¿Cómo se reprograma y quién lo registra?
10. **[P]** ¿Cómo se maneja el mantenimiento que **debe** hacerse (por norma o seguridad) frente al que es **recomendado**?
11. **[N]** ¿Qué porcentaje de las intervenciones se cumple a tiempo hoy? ¿Cuánto tarda en promedio una intervención por tipo?
12. **[V]** Confirmar con un ejemplo: "para el dron X con estas horas, el plan generaría…".

---

## 8. Bloque — Registro de horas de vuelo, ciclos y telemetría → V3, V4, V9

1. **[A]** ¿Cómo se registran hoy las horas de vuelo y los ciclos de cada dron?
2. **[P]** ¿Quién registra (piloto, sistema del dron, coordinador)? ¿En qué momento (después de cada vuelo, al final del día)? ¿Con qué formato?
3. **[P]** ¿Qué datos exactos se capturan por vuelo (fecha, dron, piloto, duración, área, producto aplicado, batería usada, incidentes)?
4. **[P]** ¿Qué entrega la **telemetría** o los logs del dron (horas de motor, ciclos de batería, voltajes, alarmas, errores)? ¿Cómo se descargan y quién los usa?
5. **[P]** ¿Esa información es confiable? ¿Qué diferencias hay entre lo que dice el dron y lo que se anota a mano? ¿Quién resuelve las discrepancias?
6. **[P]** ¿Qué hacen si faltan datos de uno o más vuelos o están mal registrados?
7. **[P]** ¿Cómo se asignan horas y ciclos a **componentes específicos** (por ejemplo a una batería o a un motor instalado en un dron)?
8. **[P]** ¿La telemetría la entrega el fabricante a través de una plataforma propia? ¿Qué restricciones o costos tiene el acceso?
9. **[N]** ¿Con qué frecuencia se actualizan los acumulados? ¿Qué desfase es aceptable?
10. **[V]** Confirmar el flujo: operación → registro → acumulado → alerta.

---

## 9. Bloque — Indicadores del proceso → V1, V6

1. **[A]** ¿Qué indicadores usan hoy para saber si el mantenimiento va bien?
2. **[N]** Para cada uno de estos indicadores, pida **fórmula exacta, fuente de datos, frecuencia, meta y responsable**:
   - **Disponibilidad de la flota** (¿cómo cuentan un dron "disponible"? ¿incluyen reservas, drones en espera de repuestos?)
   - **Cumplimiento del plan de mantenimiento** (¿a tiempo, con tolerancia?)
   - **Tiempo medio entre fallas (MTBF)** (¿qué es "falla" para ustedes? ¿por dron o por componente?)
   - **Costo de mantenimiento por hora de vuelo** (¿qué costos se incluyen: repuestos, mano de obra, transporte, indisponibilidad?)
   - Otros que usen: tiempo medio de reparación, mantenimientos correctivos vs. preventivos, rotación de repuestos, hallazgos por inspección.
3. **[P]** ¿Quién consulta cada indicador y para qué decisiones? ¿Cada cuánto?
4. **[P]** ¿Qué indicador les preocupa más hoy y por qué? ¿Qué valor tienen actualmente (aprox.)? **[N]**
5. **[P]** ¿Qué datos hoy les faltan para calcular bien alguno?
6. **[C]** Denos un ejemplo numérico de cómo se calcula uno de ellos con datos reales de un mes.
7. **[V]** Confirmar las fórmulas.

---

## 10. Bloque — Capacidades y recursos del negocio (para V2; sin pedir el mapa) → V2

> **No** pidan "el mapa de capacidades". Pregunten cómo es la empresa y deriven ustedes el mapa.

1. **[A]** ¿Qué funciones o áreas debe tener una empresa como la suya para prestar el servicio de fumigación con drones de punta a punta?
2. **[P]** Para cada una: ¿qué debe saber hacer, quién la realiza y con qué recursos?
3. **[P]** ¿Cuáles de esas funciones son el "corazón" del negocio, cuáles son estratégicas y cuáles de apoyo?
4. **[P]** ¿Qué tan maduras o fuertes son hoy (bien resueltas, informales, débiles)? ¿Cuáles están tercerizadas?
5. **[P]** ¿Qué **recursos tangibles** son críticos (flota, baterías, cargadores, herramientas, bodegas, vehículos, banco de pruebas)? ¿Y qué **recursos intangibles** (registros, certificaciones, conocimiento técnico, contratos)?
6. **[P]** ¿Cuáles de esas funciones se verían afectadas por un buen o mal mantenimiento preventivo?
7. **[P]** ¿Qué funciones de la empresa dependen de información de mantenimiento (planeación de servicios, compras, finanzas, calidad, seguridad)?
8. **[V]** Validar la lista de funciones y quién es responsable de cada una.

---

## 11. Bloque — Excepciones y situaciones difíciles → V3, V4, V6

1. **[A]** Cuéntenos las situaciones fuera de lo normal que más les han complicado el mantenimiento.
2. **[P]** ¿Qué hacen cuando:
   - un dron falla en campo durante un servicio?
   - se vence una condición de mantenimiento y el dron está comprometido con un cliente?
   - no hay repuesto y la importación tarda?
   - el técnico certificado no está disponible?
   - hay un accidente o incidente de vuelo?
   - un componente falla antes de su vida útil (falla prematura)?
   - dos drones comparten componentes y ambos requieren el mismo repuesto?
   - se detecta un dato de horas/ciclos erróneo o faltante?
   - llega un boletín o recomendación del fabricante que cambia un intervalo?
   - un componente vuelve de garantía o de reparación externa?
3. **[P]** ¿Quién decide en cada caso y con qué criterios?
4. **[P]** ¿Cómo se registra la excepción y cómo se reflejan sus consecuencias en el plan?
5. **[C]** ¿Cuál fue el peor incidente de mantenimiento que han vivido y qué cambiaron después?
6. **[V]** Confirmar las excepciones más frecuentes y su manejo.

---

## 12. Bloque — Normatividad y cumplimiento (Colombia) → V1, V4, V9

> **Importante:** la IA puede equivocarse o inventar números de normas. Todo lo que diga debe **contrastarse** con fuente oficial (ver 12.3). Pídanle siempre el **nivel de certeza**.

### 12.1 Preguntas al experto

1. **[A]** ¿Qué normas, reglamentos o autoridades regulan la operación y el mantenimiento de sus drones de fumigación en Colombia?
2. **[P]** ¿Cuál es la **autoridad aeronáutica** y qué le exige a un operador de drones agrícolas (registro de la aeronave, permisos de operación, certificados de operador o de piloto, seguros)?
3. **[P]** ¿Qué exige la norma específicamente sobre **mantenimiento** de las aeronaves no tripuladas (programas de mantenimiento, registros, inspecciones, personal autorizado)?
4. **[P]** ¿Qué registros deben llevar (bitácoras de vuelo, de mantenimiento, de componentes), **durante cuánto tiempo** y en qué formato? ¿Quién puede auditarlos?
5. **[P]** ¿Qué reportes o evidencias deben entregar a la autoridad y con qué periodicidad? ¿Qué ocurre en una inspección?
6. **[P]** ¿Cuáles son las consecuencias de incumplir (sanciones, suspensión de operación, pérdida de cobertura del seguro)?
7. **[P]** ¿Qué requisitos tienen los **técnicos** y **pilotos** (formación, certificados, vigencias)? ¿Quién los expide?
8. **[P]** ¿Qué normas aplican a la **aspersión de agroquímicos** con drones (autoridad agrícola/sanitaria, autorizaciones, restricciones de zona, registros de aplicación)? ¿Cómo se relaciona eso con el mantenimiento (por ejemplo, limpieza y calibración del sistema de aspersión)?
9. **[P]** ¿Qué normas ambientales afectan al mantenimiento (residuos de agroquímicos, baterías de litio, envases, componentes desechados)?
10. **[P]** ¿Qué normas de **seguridad y salud en el trabajo** aplican al taller y a la manipulación de baterías y productos químicos?
11. **[P]** ¿Qué exigen las **aseguradoras** (pólizas de responsabilidad civil u otras) en cuanto a mantenimiento y registros?
12. **[P]** ¿Hay normas de **protección de datos personales** que afecten los datos de pilotos, técnicos o clientes?
13. **[P]** ¿Qué parte del **manual del fabricante** es de obligatorio cumplimiento y qué parte es recomendación?
14. **[P]** ¿Qué cambios normativos recientes o previstos podrían afectar el mantenimiento en los próximos años?
15. **[N]** ¿Qué plazos normativos o límites numéricos conoce (por ejemplo, intervalos de inspección, vigencias, tiempos de conservación de registros)?
16. **[P]** Para cada obligación mencionada: ¿cuál es la **evidencia** que se debe poder mostrar (documento, registro, firma)?
17. **[V]** "Usted nos dice que [obligación] aplica a [proceso]. ¿Es norma, práctica del fabricante o criterio interno?"

### 12.2 Cómo le pregunta a la IA por incertidumbre (copiar)

```text
Para cada norma que nos mencionó, indíquenos: (1) nombre y número si lo sabe, (2) autoridad que la emite, (3) qué exige exactamente, (4) qué tan seguro está (alto/medio/bajo) y (5) qué documento oficial deberíamos consultar para verificarlo. Si no está seguro del número o del texto, dígalo.
```

### 12.3 Qué deben contrastar por su cuenta (hipótesis de partida, **a verificar**)

> [!warning] Esta lista son **pistas de investigación**, no afirmaciones. Verifiquen cada una en fuente oficial antes de usarla.

| Tema | Dónde buscar | Qué comprobar |
|---|---|---|
| Operación de aeronaves no tripuladas (RPAS/drones) | Aerocivil: Reglamentos Aeronáuticos de Colombia (RAC), en particular lo referido a RPAS (se suele citar RAC 91, apéndice sobre aeronaves no tripuladas) | Registro, permisos, certificaciones, requisitos de mantenimiento y registros, vigencia actual |
| Aviación agrícola / aspersión aérea | Aerocivil e ICA | Si hay requisitos específicos para aspersión con drones y para quienes la prestan |
| Uso y manejo de plaguicidas | ICA / Ministerio de Agricultura (existen decretos y resoluciones sobre uso, aplicación y registro de plaguicidas) | Restricciones y registros relacionados con la aplicación |
| Seguridad y salud en el trabajo | Ministerio del Trabajo (Sistema de Gestión SST) | Requisitos para taller, EPP, manipulación química y de baterías |
| Residuos y baterías | Autoridad ambiental / Ministerio de Ambiente (residuos peligrosos, pilas y acumuladores, programas posconsumo) | Cómo se disponen baterías de litio y envases |
| Protección de datos personales | Ley 1581 de 2012 y su reglamentación | Tratamiento de datos de pilotos, técnicos, clientes |
| Seguros | Pólizas y aseguradoras del sector | Cláusulas sobre mantenimiento y registros |
| Fabricantes | Manuales de mantenimiento públicos (por ejemplo de fabricantes de drones agrícolas) | Intervalos típicos por componente |

Para cada hallazgo normativo, registren: *norma · artículo/numeral · qué exige · a quién aplica · cómo impacta el software · evidencia a conservar · fuente*.

---

## 13. Bloque — Interoperabilidad (OBLIGATORIO) → V4 (ACL), V8, V9

> Para cada interlocutor, usen la **misma plantilla de preguntas** (13.0). Luego las preguntas específicas.

### 13.0 Plantilla de preguntas (repetir para cada interlocutor)

1. **[A]** ¿Cómo se relaciona el mantenimiento preventivo con [X]?
2. **[P]** ¿Qué información **sale** del mantenimiento hacia [X] y cuál **llega** desde [X]?
3. **[P]** ¿Quién inicia el intercambio y **cuándo** (evento, horario, solicitud)?
4. **[P]** ¿En qué **formato y medio** se hace (archivo, correo, llamada, formulario, plataforma)?
5. **[P]** ¿Quién es el **dueño** de ese dato y quién lo mantiene?
6. **[P]** ¿Qué **calidad** tiene el dato (completo, actualizado, confiable)?
7. **[P]** ¿Qué pasa si no llega, llega tarde o llega incorrecto?
8. **[P]** ¿Usa [X] **términos distintos** a los de mantenimiento para las mismas cosas? (¡clave para anticorrupción!)
9. **[N]** ¿Con qué frecuencia y volumen?
10. **[V]** Confirmar la tabla "qué-quién-cuándo-formato-dueño".

### 13.1 Programación de servicios a clientes
- ¿Quién programa los servicios y con qué herramienta? ¿Cómo se entera mantenimiento de los servicios próximos?
- ¿Qué información necesita mantenimiento de programación (fechas, drones asignados, horas estimadas) y qué necesita programación de mantenimiento (disponibilidad de drones, fechas de parada)?
- ¿Qué pasa cuando un servicio y una intervención programada chocan? ¿Quién decide?
- ¿Cómo se reflejan las horas de un servicio en los acumulados del dron?

### 13.2 Inventario y compras de repuestos
- ¿Qué información sale hacia inventario (repuestos requeridos por intervención, consumos) y cuál llega (existencias, ubicación, reservas, fechas de llegada)?
- ¿Cómo se disparan las compras (stock mínimo, solicitud del técnico, plan de mantenimiento)? ¿Quién las aprueba?
- ¿Cómo se registran los consumos de un repuesto en una intervención (¿se descuenta del inventario?) y quién lo hace?
- ¿Cómo se maneja la reserva de repuestos para intervenciones futuras?

### 13.3 Telemetría de los drones
- ¿Qué datos entrega la telemetría y en qué formato (logs, API del fabricante, archivos, plataforma)?
- ¿Cómo y cuándo llegan al proceso de mantenimiento? ¿Hay datos en tiempo real o por lote?
- ¿Qué tan difícil es **asociar** la telemetría con el dron y los componentes correctos? ¿Hay diferencias entre fabricantes?
- ¿Qué alarmas de la telemetría generan acciones de mantenimiento?

### 13.4 Técnicos certificados
- ¿Cómo se sabe qué técnicos están certificados para qué tareas y hasta cuándo? ¿Dónde se guarda esa información y quién la mantiene?
- ¿Qué información necesita el mantenimiento (certificaciones vigentes, disponibilidad) y qué devuelve (tareas realizadas, firmas, horas)?
- ¿Qué pasa si no hay técnico certificado disponible para una tarea?
- ¿Quién emite las certificaciones (autoridad, entidad de formación, fabricante)?

### 13.5 Autoridad aeronáutica
- ¿Qué información se reporta o se registra ante la autoridad y con qué frecuencia?
- ¿Cómo se hace (trámite en línea, formularios, inspecciones presenciales)?
- ¿Qué evidencia se entrega de mantenimiento? ¿Qué pasa si la autoridad pide una auditoría o una explicación de un evento?
- ¿La autoridad define formatos o estándares de datos que el proceso deba cumplir?

### 13.6 Otros interlocutores (preguntar si existen; confirmar, ampliar o descartar)
- **Financiero/contable:** costos de mantenimiento, activos, depreciación, facturación de servicios.
- **Fabricantes/proveedores:** boletines de servicio, garantías, soporte técnico, actualizaciones de firmware.
- **Aseguradoras:** reportes de mantenimiento, siniestros.
- **Talento humano:** vinculación, capacitación, vigencia de certificados.
- **Seguridad y salud en el trabajo / calidad / ambiental:** reportes de incidentes, residuos, auditorías.
- **Clientes:** informes de servicio, evidencia de operación.
- **Autoridad agrícola/ambiental:** registros de aplicación y de residuos.
- **Planeación agronómica / GIS / gestión de lotes.**
- **Otros que el experto mencione y que ustedes no hayan listado.**

### 13.7 Pregunta de cierre del bloque
**[A]** ¿Con qué otros procesos, áreas, sistemas o entidades se intercambia información de mantenimiento que no hayamos mencionado?

---

## 14. Bloque — Motivación y estrategia (insumos de V1) → V1

1. **[A]** ¿Quiénes son los **interesados** en que el mantenimiento funcione bien (internos y externos) y cuál es el interés de cada uno?
2. **[A]** ¿Qué **fuerzas** (internas o externas) los están empujando a mejorar o sistematizar el mantenimiento (crecimiento de flota, presión normativa, quejas de clientes, costos, accidentes, competencia)? *(driver)*
3. **[P]** ¿Qué **auditorías, incidentes, hallazgos o indicadores** actuales los preocupan? ¿Qué dicen? *(assessment)*
4. **[N]** ¿Qué quieren lograr con un mejor mantenimiento? Pidan **metas con número y fecha** (por ejemplo, disponibilidad objetivo, reducción de costos, cumplimiento del plan).
5. **[P]** ¿Cómo se vería el **resultado** concreto si lo logran? ¿Qué cambiaría en la operación? *(outcome)*
6. **[P]** ¿Qué **principios o valores** guían sus decisiones de mantenimiento (por ejemplo, seguridad por encima de productividad, trazabilidad, transparencia)? *(principle)*
7. **[P]** ¿Qué debe cumplir **sí o sí** una solución para ustedes? *(requirement)* Pidan que los prioricen: imprescindible / deseable.
8. **[P]** ¿Qué **limitaciones** tienen (presupuesto, tiempo, personal, tecnología existente, normativa)? *(constraint)*
9. **[P]** ¿Qué pasaría si **no** se hace nada? ¿Qué riesgos o costos aparecen?
10. **[P]** ¿Quién decide, quién aprueba el presupuesto y quién se opone al cambio?
11. **[V]** Resumir en una tabla "interesado → impulsor → meta" y confirmar.

---

## 15. Bloque — Alcance: qué entra y qué no (sin pedir diseño) → V2, V4

> Aquí se trata de **entender fronteras de negocio**, no de diseñar. Las decisiones de alcance las toma el equipo con lo que la IA aporte.

1. **[A]** Cuando dicen "mantenimiento preventivo", ¿qué actividades incluyen exactamente? ¿Qué **no** incluyen?
2. **[P]** ¿Qué hacen con el mantenimiento **correctivo** (reparaciones por falla)? ¿Lo gestiona la misma persona o área? ¿Debería quedar fuera?
3. **[P]** ¿Quién es el dueño hoy de: la **programación de servicios**, el **inventario**, las **compras**, la **telemetría**, la **gestión de personal certificado** y el **reporte a la autoridad**? ¿Son del área de mantenimiento o de otras áreas?
4. **[P]** De las 5 funciones que desean del software (horas y ciclos, despiece y condiciones, repuestos y consumibles, plan de mantenimiento, indicadores): ¿cuál es la **más urgente**? ¿Cuál puede esperar?
5. **[P]** ¿Qué decisiones debe **apoyar** el software y cuáles seguirán siendo humanas?
6. **[P]** ¿Quiénes serían los **usuarios** del software y qué espera cada uno?
7. **[P]** ¿Qué funciones **ya están resueltas** por otros sistemas o personas y no deben duplicarse?
8. **[P]** ¿Qué flota cubriría (todos los drones, solo algunos modelos) y qué tipos de mantenimiento (solo los de calendario, también por horas/ciclos/estado)?
9. **[P]** ¿Qué considerarían una **solución exitosa** a un año?
10. **[P]** ¿Qué NO esperan que haga el software (por ejemplo, planificar vuelos, facturar, gestionar nómina)?
11. **[V]** Resumir "dentro del alcance / fuera del alcance / por definir" y pedir confirmación.

### 15.1 Tabla de zonas grises (para que el equipo la complete con lo que respondan)

| Tema | ¿Lo hace el proceso de mantenimiento? | ¿Lo hace otra área/sistema? | Decisión del equipo | Justificación |
|---|---|---|---|---|
| Correctivo | | | | |
| Programación de servicios a clientes | | | | |
| Compras y stock | | | | |
| Telemetría | | | | |
| Certificación de técnicos | | | | |
| Reporte a la autoridad | | | | |
| Costos y contabilidad | | | | |
| Gestión de garantías | | | | |

---

## 16. Bloque — Cierre y validación

1. **[V]** Recapitulación guiada de cada bloque: "Esto es lo que entendimos… ¿qué corregiría?".
2. **[P]** ¿Qué no preguntamos y debimos preguntar?
3. **[P]** ¿Qué documentos, formatos o ejemplos reales podría compartirnos (bitácoras, planes, formatos de órdenes de trabajo, reportes de indicadores)?
4. **[P]** ¿Qué errores comunes cometen los equipos que intentan sistematizar el mantenimiento preventivo?
5. **[P]** ¿Qué es lo primero que le pediría a este software?
6. **[V]** Pedir un **resumen final** de los supuestos y puntos inciertos para registrarlos como supuestos (S-xx).

---

## 17. Preguntas de verificación de consistencia (hacer en otra sesión)

Repreguntar con otras palabras para detectar contradicciones:

1. ¿Cuántos drones tiene y de qué modelos? (compárenlo con sesión 1)
2. ¿Cada cuánto se cambia [componente X] y por qué criterio? (compárenlo con la tabla de la sesión 2)
3. ¿Quién libera un dron después de mantenimiento?
4. ¿Cómo se calcula la disponibilidad de la flota?
5. ¿Cuántos técnicos certificados hay y qué certificaciones tienen?
6. ¿Qué pasa si se vence una condición con el dron comprometido?

Si la IA responde distinto, **pidan que explique la diferencia** y registren el cambio como hallazgo ajustado.

---

## 18. Preguntas PROHIBIDAS (diseño) y cómo redirigir

| No preguntar                                     | Preguntar en su lugar                                                           |
| ------------------------------------------------ | ------------------------------------------------------------------------------- |
| "¿Cuál es el mapa de capacidades de la empresa?" | "¿Qué funciones debe tener una empresa como la suya y quién las realiza?"       |
| "¿Cuáles son los dominios/subdominios?"          | "¿Dónde cambia el lenguaje o la responsabilidad entre áreas?"                   |
| "¿Cuáles son los agregados/entidades?"           | "¿Qué información se maneja de un componente y qué reglas no se pueden romper?" |
| "¿Cómo sería el mapa de contextos?"              | "¿Con quién intercambia información y de qué manera?"                           |
| "¿Qué servicios debería tener el software?"      | "¿Qué actividades debe poder hacer el equipo con el software?"                  |
| "Dibuje la vista ArchiMate"                      | (No pedir diagramas)                                                            |

**Si la IA se pasa de rol y propone diseño** (copiar):
```text
Gracias, pero el diseño de arquitectura es parte de nuestro trabajo. Volvamos al negocio: cuéntenos cómo funciona hoy [tema], quién lo hace y con qué información.
```

---

## 19. Plantilla para registrar hallazgos durante la sesión

| ID | Bloque/pregunta | Hallazgo (cita resumida) | Tipo (regla / cifra / actor / norma / dato / excepción) | Certeza de la IA | A contrastar con | Vista que alimenta |
|---|---|---|---|---|---|---|
| H-01 | 5.7 | | | Alta/Media/Baja | | V6 |

**Etiquetas de revisión posterior:** Aceptado · Ajustado · Descartado · Supuesto.

---

## 20. Checklist de cobertura (¿ya sabemos todo lo necesario?)

- [ ] Negocio: clientes, flota, temporadas, organigrama, herramientas actuales.
- [ ] Proceso E2E con eventos, actores, bifurcaciones y excepciones.
- [ ] Despiece y condiciones con umbrales y fuentes para ≥ 5 componentes.
- [ ] Repuestos/consumibles por tipo de cambio, stock, proveedores, garantía, disposición.
- [ ] Plan: quién lo define, cómo se programa, cómo se concilia con servicios, qué pasa si no se cumple.
- [ ] Horas/ciclos/telemetría: origen, formato, calidad, frecuencia.
- [ ] Indicadores con **fórmula, fuente, frecuencia, meta, responsable**.
- [ ] Capacidades y recursos de **toda** la empresa.
- [ ] Normatividad: autoridad, obligaciones, registros, plazos, consecuencias; **contrastada** con fuente oficial.
- [ ] Interoperabilidad: los 5 interlocutores del enunciado confirmados/descartados + otros; dirección, información, frecuencia, formato, dueño.
- [ ] Motivación: interesados, impulsores, evaluaciones, metas con número y fecha, resultados, principios, requerimientos, restricciones.
- [ ] Alcance: dentro / fuera / por definir, con justificación.
- [ ] Pruebas de consistencia realizadas.
- [ ] Conversaciones exportadas completas y hallazgos registrados.

