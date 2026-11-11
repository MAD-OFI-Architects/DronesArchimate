---
tags: [proyecto, fase-0, drones, hallazgos, contraste]
aliases: [Análisis de hallazgos Fase 0, Hallazgos entrevista Pompilio]
---

# 05 · Análisis de hallazgos — Fase 0 (Pasos 5 y 6)

> **Qué es este documento:** el análisis del equipo exigido por el enunciado: *qué hallazgos se aceptaron, cuáles se descartaron o contrastaron con otras fuentes y cómo influyeron en el diseño*.
>
> **Cómo se contrastó:** (1) fuentes oficiales colombianas (aerocivil.gov.co, minambiente.gov.co, MinTrabajo, Invima/FAOLEX), (2) manuales y especificaciones del fabricante (dji.com, xa.com, guía de mantenimiento DJI Agras y manual del T40 disponible vía filings de la FAA), (3) literatura técnica y de mercado del sector.
>
> **Clasificación:** **Aceptada** (coincide / es razonable) · **Contrastada y ajustada** (parcialmente correcta) · **Descartada** (incorrecta o no aplica) · **Pendiente** (no verificable → queda como supuesto S-xx).
>
> Las referencias S1–S5/P## remiten a `04_entrevista_organizada.md` (Sesión / Pregunta). El impacto se traza a las vistas V1–V11 (V1 motivación · V2 capacidades · V3 E2E · V4 servicios/ACL · V5 dominios · V6 agregados · V7 glosario · V8/V9 contextos e interoperabilidad · V10 trazabilidad · V11 canvas).

---

## Paso 5 — Contraste con fuentes externas

### 5.1 Normatividad colombiana

| # | Afirmación del experto (ref.) | Fuente consultada | Resultado | Clasif. |
|---|---|---|---|---|
| C-01 | La operación de drones está reglamentada por la Aerocivil en el **RAC 100** con plataforma **UAS Colombia**; registro obligatorio desde 200 g; categorías de operación (abierta/específica) (S3/P111–P112) | aerocivil.gov.co (Reglamentos Aeronáuticos; campañas "Vuela Legal, Vuela Seguro"); guías del sector | **Confirmado.** El RAC 100 reglamenta la operación de UAS; registro en plataforma UAS Colombia desde 200 g; categorías abierta/específica; operación agrícola en categoría con requisitos adicionales | |
| C-02 | "Del número y fecha de la resolución que adopta el RAC 100 no me consta" (S3/P111, P124) | aerocivil.gov.co → *Resoluciones a los RAC*: **Resolución 0334 del 27-dic-2024** adopta el RAC 100; aclarada por **Resolución 00077 del 14-ene-2025** | **Precisado:** ahora se tiene número y fecha exactos para citar en V1 | |
| C-03 | **Seguro de responsabilidad civil** exigido para operar (S1/P25, S3/P121) | Comunicaciones oficiales de la Aerocivil (póliza RC frente a terceros); oferta aseguradora colombiana (pólizas RC drones) | **Confirmado** para operación comercial/profesional, con matices por categoría y peso. El condicionado exacto sigue siendo lectura pendiente | |
| C-04 | Certificado/licencia de **piloto UAS** (idoneidad) exigido (S1/P23, S3/P112) | RAC 100 — Capítulo G (§100.600 y ss.): Certificado de Idoneidad para Pilotos UAS en categoría específica | **Confirmado.** Vigencias exactas de renovación: seguir como supuesto | |
| C-05 | "No existe licencia estatal de **técnico de mantenimiento** de drones" (S1/P23, S3/P117) | Búsqueda en normatividad RAC 100: el foco es pilotos y operadores; no se encontró licencia de técnico de mantenimiento UAS | **Sin evidencia ni a favor ni en contra.** Mantener como supuesto; verificar con la Aerocivil o el distribuidor | → S-04 |
| C-06 | **Decreto 1843 de 1991** regula el uso de plaguicidas; su aplicabilidad a la aspersión con drones "habría que verificarla con el ICA" (S3/P118) | Invima, FAOLEX, compilaciones normativas | **Vigente** y regula uso, manejo y aplicación (incluida aérea) de plaguicidas — pero su capítulo de aplicación aérea es anterior a los UAS (orientado a aviación tripulada). Aplicabilidad literal a drones: por confirmar con el ICA | |
| C-07 | Posconsumo de **envases** de plaguicidas: devolución al comercializador (Resolución 1675 de 2013) (S3/P119) | Ministerio de Ambiente; compilaciones de posconsumo | **Confirmada.** Resolución 1675 de 2013, programa posconsumo de envases y empaques de plaguicidas | |
| C-08 | Posconsumo de **pilas y baterías**: Resolución 1297 de 2010; "salió regulación nueva y no sé si cubre litio" (S3/P119) | minambiente.gov.co; Alcaldía de Bogotá; registro de normas | **1297/2010 confirmada** (sistemas de recolección de pilas y acumuladores). La **Resolución 0799 de 2025** reglamenta la recolección de baterías usadas (centrada en plomo-ácido); alcance a baterías de litio: **por verificar** | + → S-05 |
| C-09 | **SST**: SG-SST (Decreto 1072 de 2015) y estándares mínimos (Resolución 0312 de 2019) (S3/P120) | Ministerio del Trabajo | **Confirmadas** y vigentes | |
| C-10 | **Ley 1581 de 2012** de protección de datos personales (S3/P122) | Norma conocida; reglamentación SIC | **Confirmada** | |
| C-11 | Plazos de **retención de registros** (bitácoras/OT) "no me constan" (S1/P114, S3/P125) | Texto del RAC 100 no leído a detalle aún | **Pendiente** de lectura del capítulo respectivo | → S-03 |

### 5.2 Técnica — manuales y especificaciones del fabricante

| # | Afirmación del experto (ref.) | Fuente consultada | Resultado | Clasif. |
|---|---|---|---|---|
| C-12 | Batería se retira a **~800–1.000 ciclos** o salud < 80 % (S2/P46) | Especificaciones de la batería DJI (DB1560/BAX601, 30.000 mAh): vida nominal de **1.000–1.500 ciclos** según la fuente (distribuidores DJI anuncian 1.500; otras fichas, 1.000) | **Ajustada:** el umbral interno de retiro es más conservador que la vida nominal del fabricante. Se mantiene el criterio interno (documentado como propio) con tope duro ≤1.000 ciclos y primacía del criterio de salud | |
| C-13 | La batería del T40 es la **"DB1560"** (S2/P46) | dji.com/t40/specs: la batería del T40 es la **BAX601-30000mAh-52.22V**; la DB1560 es la línea T30/T40/T50 según distribuidores (compatibilidad comercial confirmada) | **Ajustada:** para el catálogo de componentes se usa **BAX601** como batería original del T40; DB1560 como compatible | |
| C-14 | Motores: inspección cada 100 h; **cambio ~300 h** o por vibración (S2/P46) | Manual DJI Agras T40 (vía filing FAA) y guías de mantenimiento DJI: primera inspección ~a los 100 vuelos/horas, inspección cada ~100 h; reemplazo recomendado hacia las **500–1.000 h** (las fuentes difieren; el número exacto debe tomarse del manual vigente) | **Ajustada:** el cambio interno a 300 h es mucho más conservador que la recomendación del fabricante. Se conserva como criterio interno explícito (flota sometida a polvo/urera), registrando la **fuente del intervalo** (manual vs. interna) como dato de primera clase | |
| C-15 | Hélices: revisión 25 h; cambio ~100 h o por golpe; **cambio en pares** con tornillos nuevos (S2/P46, P57) | Guía oficial DJI "Agras T40 Preseason Maintenance": reemplazo de hélices **en pares junto con empaques nuevos**; inspección antes de cada vuelo | **Confirmada** la práctica (pares + empaques); el ciclo exacto de reemplazo por horas queda por el manual vigente | (+ S-02) |
| C-16 | La plataforma DJI cuenta **ciclos y salud por ID de batería** (S2/P83, P86) | Plataforma DJI Agriculture / fichas de la batería inteligente | **Confirmado** | |
| C-17 | T40: tanque 40 L, 8 motores coaxiales (2 por brazo), 2 boquillas de atomización (S1/P2, S2/P40) | dji.com/t40/specs (carga útil 50 kg, doble rotor coaxial) | **Confirmado** | |
| C-18 | XAG P100 Pro: tanque 50 L (S1/P2) | xa.com/en/p100pro (payload 50 kg) | **Confirmado** | |
| C-19 | El fabricante ofrece un **servicio de gestión de flota en la nube, de pago, no contratado**; la telemetría se descarga manual (S2/P83, P87) | DJI (FlightHub Pro / DJI Agriculture) | **Confirmado:** existen servicios de pago; la empresa usa la plataforma básica con exportación manual | |

### 5.3 Cifras de negocio y de operación

| # | Afirmación del experto (ref.) | Fuente consultada | Resultado | Clasif. |
|---|---|---|---|---|
| C-20 | Tarifa de referencia **$40.000–$70.000 COP/ha** (S1/P5) | Referencias de mercado del sector (≈ 12 USD/ha ≈ $45–60 mil COP; grupos gremiales) | **Ajustada:** rango razonable pero la banda alta queda por encima del mercado típico; se usa $40–60 mil como rango realista, con la banda alta solo para servicios especiales | |
| C-21 | ~15.000 ha/año con ~2.000 h de flota → **7,5 ha/h efectiva** (S1/P3, P14) | Aritmética interna vs. especificaciones (T40: hasta ~16–21 ha/h brutas teóricas) | **Consistente** con eficiencia de campo realista (traslados, recargas, lotes pequeños) | |
| C-22 | El correctivo cuesta **2–3 veces** el preventivo (S1/P6) | Literatura de gestión de mantenimiento (la regla común sitúa el correctivo/emergente entre 3–5× el planificado) | **Razonable** (incluso optimista) | |
| C-23 | Disponibilidad = **dron-días verdes / dron-días** (S3/P91, P95) | Fórmula estándar de disponibilidad | **Razonable.** El hueco real es la regla de conteo (donantes dentro/fuera) — eso es decisión de diseño, no de contraste | |
| C-24 | Corrosión por agroquímicos y obstrucción por sólidos (urera) son el desgaste dominante; el **lavado** es mantenimiento diario (S1/P17–P18) | Guías de mantenimiento DJI Agras (limpieza post-aplicación como tarea crítica) | **Confirmado** | |

**Balance del contraste:** 16 · 6 · 0 · 5 (S-02…S-08).
No hubo hallazgos **descartados**: el experto no afirmaba datos normativos que pudieran resultar falsos (marcaba su nivel de certeza y remitía a la fuente oficial), así que lo que no se pudo verificar quedó como supuesto en lugar de resultar falso.

---

## Paso 6 — Tabla de hallazgos y su impacto en el diseño

> Criterio de impacto: cada hallazgo se traza al elemento de diseño que lo origina. "—" en fuente de contraste = hallazgo interno del negocio, aceptado como realidad de la empresa (no requiere contraste externo).

| ID | Hallazgo (cita resumida) | Sesión/pregunta | Tipo | Decisión | Fuente de contraste | Impacto en el diseño (vista / elemento) |
|---|---|---|---|---|---|---|
| H-01 | Flota de 12 drones, **dos marcas** (DJI/XAG), IDs internos ADV-01..12, antigüedad 1–6 años | S1/P2 | dato | Aceptado | — | V5/V6: entidad **Dron** con modelo/marca; el **plan nace por modelo** y se ajusta por dron. V7: *Dron*, *Modelo*, *ID interno* |
| H-02 | Drones ≥200 g **registrados ante la Aerocivil** (UAS Colombia); operación agrícola en categoría específica | S3/P112 | norma | Aceptado | Aerocivil — RAC 100 / UAS Colombia | V1: restricción regulatoria; V9: ACL con Autoridad aeronáutica; V7: **Registro oficial ≠ ID interno** (homónimo) |
| H-03 | RAC 100 adoptado por **Res. 0334 del 27-dic-2024**, aclarada por Res. 00077/2025 | S3/P124 | norma | Precisado | aerocivil.gov.co (Resoluciones a los RAC) | V1: restricción con cita verificable; V10: trazabilidad requisito→norma |
| H-04 | Pilotos con **Certificado de Idoneidad UAS** (cap. G del RAC 100); vigencias en carpetas de administración | S1/P23, S3/P117 | norma | Aceptado | RAC 100 | V3/V4: rol **Piloto remoto** con requisito de certificación; V9: ACL con gestión de personal; V1: restricción |
| H-05 | **Seguro RC obligatorio**; en siniestros la aseguradora pide evidencia de mantenimiento | S1/P25, S3/P121 | norma | Aceptado | Aerocivil (comunicados) + oferta aseguradora | V1: restricción y stakeholder *Aseguradora*; V4: servicio "Generar evidencia de mantenimiento"; V9: ACL Aseguradora |
| H-06 | "No existe licencia estatal de **técnico de mantenimiento** de drones" | S1/P23, S3/P117 | norma | Pendiente | Sin evidencia (S-04) | V4: la función *Gestión de certificaciones* queda **por definir** (incluir/excluir); no se modela como restricción |
| H-07 | **Decreto 1843/1991** (plaguicidas): vigente, pero capítulo aéreo previo a los UAS | S3/P118 | norma | Ajustado | Invima/FAOLEX | V1: restricción sanitaria "a precisar con ICA"; V3: la **calibración de dosis** (probeta) se liga a cumplimiento, no solo a técnica |
| H-08 | Posconsumo de **envases** (Res. 1675/2013): devolución al comercializador | S3/P119 | norma | Aceptado | MinAmbiente | V9: ACL con gestor/agroinsumo; V6: disposición de consumibles al cerrar ciclo de vida |
| H-09 | Posconsumo de **baterías** (Res. 1297/2010; nueva Res. 799/2025, alcance litio por verificar) | S3/P119 | norma | + S-05 | MinAmbiente | V6: estado **Retirada** → disposición con certificado; V9: ACL ambiental |
| H-10 | SST: SG-SST (D. 1072/2015) + estándares (Res. 0312/2019) | S3/P120 | norma | Aceptado | MinTrabajo | V1: restricción; V3: tareas con EPP/capacitación anual |
| H-11 | **Ley 1581/2012** aplica a datos de pilotos/técnicos/clientes | S3/P122 | norma | Aceptado | Ley 1581/2012 | V1: restricción de privacidad; V9: frontera de datos personales |
| H-12 | Plazo de **retención de registros** desconocido | S1/P114, S3/P125 | norma | S-03 | RAC 100 por leer | V6: el historial de OT/bitácoras debe ser consultable y exportable (auditoría) — parámetro de retención configurable |
| H-13 | Batería: retiro ~800–1.000 **ciclos** o salud <80 %; nominal del fabricante 1.000–1.500 | S2/P46 | cifra | Ajustado | Specs DJI (DB1560/BAX601) | V6: condición **por ciclos** + condición **por estado (salud)** en *Componente*; el umbral lleva atributo **fuente** (manual/interna) y es configurable. V7: *Ciclo de carga* |
| H-14 | La batería del T40 es BAX601 (no "DB1560" como decía el experto) | S2/P46 | dato | Ajustado | dji.com/t40/specs | V5/V6: **catálogo de componentes por modelo** (BAX601 original; DB1560 compatible) |
| H-15 | Motores: inspección 100 h; cambio interno 300 h vs. 500–1.000 h del fabricante | S2/P46 | cifra | Ajustado | Manual DJI T40 (filing FAA) + guías DJI | V6: umbral por **horas** con *fuente del intervalo* (manual vs. interna) como atributo; V4: servicio de **parametrización del plan** |
| H-16 | Hélices: cambio en **pares** con empaques nuevos; por horas o por golpe | S2/P46, P57 | cifra | Aceptado | Guía DJI preseason (S-02 para el número exacto) | V6: condición mixta **horas + estado**; V4: *kit de repuestos* (hélice ×2 + empaques) |
| H-17 | Con varias condiciones, manda **"lo que ocurra primero"** | S2/P47 | regla | Aceptado | Práctica estándar de mantenimiento | V6: **invariante** de la condición compuesta de *Componente* |
| H-18 | **"Ciclo" polisémico**: batería=ciclo de carga; dron=horas; bomba/tanque=cargas de caldo | S2/P48 | lenguaje | Aceptado | — | V7: término **homónimo por contexto** (exigido ≥2 en el glosario); V5: frontera de lenguaje entre subdominios |
| H-19 | Tareas **críticas no se difieren** jamás; menores ≤10 % con firma del jefe | S2/P49–P50 | regla | Aceptado | — | V6: invariante de *Orden de trabajo* (estado) y regla de vencimiento; V4: servicio **"Diferir intervención"** con autorización; V1: principio *seguridad > productividad* |
| H-20 | El "reloj" es **del componente, no del dron**; el arrastre hoy es manual y frágil | S2/P36, P51 | regla | Aceptado | — | V6: **Dron** y **Componente instalado** como unidades con contadores propios; evento *Componente instalado/desmontado* con **horas de corte** |
| H-21 | Las baterías viven en **pool** y rotan entre drones (identidad propia por ID) | S2/P44 | dato | Aceptado | Plataforma DJI | V6: *Componente* con identidad e historial **independiente del dron** (evidencia para decidir si Dron y Componente instalado son agregados separados) |
| H-22 | **Quien ejecuta no libera** (en mayores); el cargo de inspector no existe — debilidad confesa | S1/P24, S2/P34 | regla/debilidad | Aceptado | Principio de mantenimiento aeronáutico | V4/V6: **Liberación** como paso con rol distinto y firma; estados de la OT; V1: principio formalizado |
| H-23 | Liberación de mayores exige **vuelo de prueba** (5–10 min) con revisión de vibraciones | S1/P24 | dato | Aceptado | — | V3: paso E2E; V6: comando *Liberar dron* con precondición "prueba OK" |
| H-24 | Registro en **3 canales** (app, papel, WhatsApp) con desfase de 2–4 días en pico | S1/P10, S2/P80–P81 | dato/dolor | Aceptado | — | V3: cuello de botella del proceso; V4: servicio **"Registrar operación"** (entrada única); V1: assessment *consolidación tardía* → meta "horas el mismo día" |
| H-25 | Para mantenimiento manda la **plataforma**; para facturar manda el **informe firmado** | S2/P84 | regla | Aceptado | — | V9: dueño del dato por propósito; V4/V8: ACL Telemetría traduce y no manda en facturación |
| H-26 | **"Horas de motor" ≠ "horas de vuelo"** (pruebas de banco también suman motor) | S2/P130 | lenguaje | Aceptado | Plataforma DJI | V7: dos términos distintos en glosario; V4: la ACL Telemetría **traduce** horas de motor → horas de vuelo |
| H-27 | Mix actual 55 % preventivo / 40 % correctivo / 5 % condición; correctivo 2–3× más caro | S1/P6, S2/P30 | cifra | Aceptado | Literatura de mantenimiento | V1: assessment + **meta correctivo ≤25 % (2028)**; V2: capacidad de gestión de flota impactada |
| H-28 | Disponibilidad = dron-días verdes / dron-días; **regla de conteo ambigua** (donantes) | S3/P91, P95 | regla | + decisión de diseño | Fórmula estándar | V6: invariante de conteo **única** (a definir por el equipo: incluir donantes o excluirlos); V1: meta ≥92 % pico 2027 |
| H-29 | Caso ADV-02: 3 semanas sin brazo por importación; creó **stock mínimo** y regla "no dos gemelos en taller" | S1/P19, S2/P59 | caso | Aceptado | — | V1: driver/assessment; V4: ACL con compras/importaciones; V6: **reserva de repuesto** para OT programada |
| H-30 | Lead times: distribuidor 1–3 días; importación 2–6 semanas | S2/P59–P60 | cifra | Aceptado | — (razonable) | V4: parámetro de **punto de reposición**; V9: ACL proveedores |
| H-31 | Tarifa $40–70 mil COP/ha | S1/P5 | cifra | Ajustado | Mercado (~12 USD/ha) | V1: modelo de ingresos con rango realista $40–60 mil (S-07) |
| H-32 | ~15.000 ha/año con ~2.000 h (7,5 ha/h efectiva); T40 60–100 ha/día | S1/P3, P14 | cifra | Aceptado | Aritmética vs. specs DJI | V2/V3: dimensionamiento de la operación; V1: contexto del negocio |
| H-33 | T40: 40 L, 8 motores coaxiales, 2 boquillas; XAG P100 Pro 50 L | S1/P2, S2/P40 | dato | Aceptado | dji.com / xa.com | V5/V6: catálogo por modelo (subsistemas y componentes) |
| H-34 | Químicos dominan el desgaste: **lavado diario** y filtros son mantenimiento | S1/P17–P18 | técnico | Aceptado | Guías DJI | V3: tareas diarias del proceso E2E; V6: condición **por estado** + tarea de limpieza en el plan |
| H-35 | Gestión de flota del fabricante (pago) **no contratada**; telemetría con export manual | S2/P83, P87 | dato | Aceptado | DJI (FlightHub/Agriculture) | V8/V9: **Telemetría = sistema externo** vía ACL (no se construye); restricción técnica "sin API pagada" en V1 |
| H-36 | Homónimos de interoperabilidad: *disponible*, *servicio/misión*, *salida/consumo*, *stock*, *certificado*, *registro/matrícula*, *bitácora* | S3/P128–P132 | lenguaje | Aceptado | — | V7: glosario con homónimos por contexto; V4/V8: cada traducción es una regla de la **ACL** |
| H-37 | Metas con número y fecha: disponibilidad ≥92 % (pico 2027), plan ≥85 % (2S-2027), correctivo ≤25 % (2028), horas mismo día (mes 1), costo/hora −15 % (2028) | S4/P138 | decisión | Aceptado | — | V1: **Goals/Outcomes** con número y fecha (regla del profesor); V10: trazabilidad requerimiento→meta |
| H-38 | Alcance: dentro = horas/ciclos, plan/condiciones, OT+repuestos, liberación, indicadores, stock del taller; fuera = misiones, facturación, nómina, contabilidad, telemetría y programación comercial (**solo se consumen**); correctivo **dentro del registro** | S4/P146–P156 | decisión | Aceptado | — | V4: tabla de **inclusión/exclusión** con justificación; V8: contextos vecinos (Programación, Inventario, Telemetría, Personal, Autoridad) con patrón de relación |
| H-39 | Firmware **congelado en campaña**, actualización en diciembre | S2/P53 | práctica | S-08 | — | V4: servicio "Actualizar firmware" por calendario; supuesto de negocio (razonable, no verificable) |
| H-40 | Exigencias exactas de **mantenimiento y registros** en el RAC 100 no leídas por el experto | S3/P113 | norma | S-03 | RAC 100 por leer | V1: restricción regulatoria a precisar antes de V4/V9; parámetros de auditoría configurables |

---

## Supuestos registrados (S-xx)

| ID | Supuesto | Origen | Cómo se validaría |
|---|---|---|---|
| S-01 | La "certificación" de técnicos = cursos del fabricante/distribuidor (sin licencia estatal) | H-06 () | Consulta a la Aerocivil (gdmua@aerocivil.gov.co) o al distribuidor DJI |
| S-02 | Ciclo exacto de reemplazo de hélices y motores según manual DJI vigente | C-14/C-15 (/) | Manual de usuario T40 (DJI) — tabla de mantenimiento |
| S-03 | El RAC 100 exige registros de mantenimiento/vuelo y un plazo de retención determinado | H-12/H-40 () | Lectura del RAC 100 (aerocivil.gov.co), capítulos de registros/operador |
| S-04 | No se exige licencia estatal de técnico de mantenimiento UAS | C-05 () | Igual que S-01 |
| S-05 | La Res. 799/2025 (baterías usadas) alcanza las baterías de litio de la flota | C-08 () | MinAmbiente / autoridad ambiental regional (CVC, Cortolima, CRC) |
| S-06 | El Decreto 1843/1991 aplica a la aspersión con UAS en los mismos términos que a la aviación tripulada | C-06 () | Concepto o norma del ICA sobre aplicación aérea con drones |
| S-07 | Tarifa realista del mercado: $40–60 mil COP/ha (banda alta solo casos especiales) | C-20 () | Cotizaciones de referencia del sector |
| S-08 | Congelar firmware en campaña es seguro y suficiente | H-39 () | Boletines de seguridad DJI / criterio del distribuidor |

---

## Cobertura del alcance de la solicitud

Verificación de que la entrevista cubre el alcance solicitado y de dónde salen los insumos de diseño:

| Requisito de la solicitud | Cobertura en la entrevista | Hallazgos asociados |
|---|---|---|
| Registro de horas de vuelo y ciclos por dron a partir de las operaciones | Bloque 2 (origen de los datos en la operación) y Bloque 8 (registro, telemetría, consolidación, desfases) | H-24, H-25, H-26, H-35 |
| Despiece con condiciones por horas, ciclos, calendario o estado | Bloque 5: despiece por subsistema, tabla componente-condición-umbral-tarea-repuesto, definición de ciclo por componente | H-13 a H-21, H-33, H-34 |
| Repuestos y consumibles por cada cambio | Bloque 6: repuestos por tipo de cambio, kits, stock mínimo, costos | H-16, H-29, H-30 |
| Plan de mantenimiento que programa intervenciones | Bloque 4 (proceso E2E) y Bloque 7 (plan, programación semanal, tolerancias, diferimientos, agrupación de tareas) | H-15, H-17, H-19, H-23 |
| Indicadores: disponibilidad, cumplimiento, MTBF, costo por hora | Bloque 9: fórmula, fuente, frecuencia y valor actual de cada indicador | H-27, H-28, H-37 |
| Interoperabilidades (programación de servicios, inventario y compras, telemetría, técnicos certificados, autoridad aeronáutica) | Bloque 13: una entrada por interlocutor con información intercambiada, dirección, formato, dueño y frecuencia; las cinco confirmadas | H-04, H-29, H-30, H-35, H-36, H-38 |

**Fronteras del alcance identificadas en la entrevista** (a argumentar en la fase de servicios):

- El mantenimiento **correctivo** no está en la solicitud. El experto recomendó registrarlo en el mismo historial (Sesión 4, P147); registrar no equivale a gestionar: la decisión de alcance la toma el equipo.
- La solicitud pide repuestos **para cada cambio**, no la gestión del inventario: inventario y compras quedan como interoperabilidad (Sesión 3, P129), no como función a construir.
- La **operación de vuelo** está fuera: el sistema registra sus resultados (horas y ciclos), no planifica misiones (H-38).
- La **telemetría** y la **programación comercial** solo se consumen vía capa anticorrupción (H-35, H-38).
- Los bloques de entrevista que exceden el alcance del software (contexto del negocio, normatividad, motivación, funciones de toda la empresa) responden a lo exigido para el mapa de capacidades del negocio completo y la vista de motivación; no agregan funciones al software.

## Resumen del análisis

**Balance:** 40 hallazgos — 29 aceptados, 6 contrastados y ajustados, 0 descartados y 5 pendientes registrados como supuestos (S-01 a S-08). No hubo hallazgos descartados porque el experto, en temas normativos, no afirmaba datos que pudieran resultar falsos: marcaba su nivel de certeza y remitía a la fuente oficial; lo que no se pudo verificar se registró como supuesto.

**Insumos para las fases de diseño:**
- **V1 (motivación):** stakeholders (H-05, H-27), drivers (H-29, H-24), assessments (H-24, H-27, H-29), metas con número y fecha (H-37), restricciones normativas citables (H-02, H-03, H-05, H-07, H-10, H-11) y técnicas (H-35).
- **V3 (E2E):** proceso de 6 etapas (S2/P29), cuello de botella (H-24), tareas diarias (H-34), vuelo de prueba (H-23).
- **V4 (servicios/ACL):** inclusión/exclusión semilla (H-38), servicios con nombre de negocio (registrar operación, diferir intervención, parametrizar plan, generar evidencia), 5+ externos con dirección/formato/dueño (S3/B13).
- **V5/V6 (dominios/agregados):** evidencia para separar *Dron* de *Componente instalado* (H-20, H-21), condiciones con fuente (H-13, H-15, H-17), invariantes (H-17, H-19, H-28), catálogo por modelo (H-14, H-33).
- **V7 (glosario):** homónimos documentados (H-18, H-26, H-36) — supera el mínimo de 2.
- **V8/V9 (contextos/interoperabilidad):** externos confirmados (H-02, H-05, H-08, H-09, H-30, H-35) con traducciones de ACL.
