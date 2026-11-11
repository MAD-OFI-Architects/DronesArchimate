---
tags: [proyecto, entrevista, fase-0, drones, conversacion]
aliases: [Entrevista Pompilio, Conversación AgroDrones del Valle]
---

# Entrevista a Pompilio Ospina — AgroDrones del Valle S.A.S.

> **Conversación con el experto (Fase 0).** Rol: Pompilio Ospina, Jefe de Operaciones y Mantenimiento, 12 años de experiencia (los últimos 6 en aviación agrícola no tripulada y mantenimiento de flotas).
> Documentos relacionados: `01_guion_entrevista.md` (guion), `02_instruccion_de_rol.md` (instrucción de rol) y `05_analisis_hallazgos.md` (análisis del equipo).
>
> **Convenciones de este documento:**
> - Cada pregunta se añade **al final** con numeración corrida (P1, P2, …), junto con su respuesta completa.
> - En temas normativos (Aerocivil, ICA, ambientales, SST, seguros) el experto indica su **nivel de certeza (alto/medio/bajo)** y distingue entre **norma**, **recomendación del fabricante** y **práctica interna**.
> - El experto habla solo del **negocio**: no propone capacidades, dominios, agregados, contextos ni arquitectura.
> - Los datos fijos de abajo son la "biblia": no cambian entre sesiones.

---

## Biblia de la empresa (datos fijos)

| Dato | Valor |
|---|---|
| **Empresa** | AgroDrones del Valle S.A.S., fundada en 2018. Galpón propio en Palmira (Valle del Cauca) con taller y bodega de repuestos. |
| **Flota** | 12 drones: 5 DJI Agras T40 (2022–2025), 4 DJI Agras T30 (2021), 2 DJI Agras T16 (2020, los más viejos) y 1 XAG P100 Pro (2023, prueba piloto). Antigüedad entre 1 y 6 años. Identificación interna pintada en los brazos: ADV-01 a ADV-12. |
| **Operación** | Valle del Cauca (caña de azúcar), norte del Cauca (palma y plátano) y norte del Tolima (arroz y maíz). ~15.000 hectáreas fumigadas al año, ~2.000 horas de vuelo de flota al año. Picos: marzo–mayo y septiembre–noviembre (siembras/lluvias); la caña se trabaja casi todo el año. |
| **Personal** | 8 pilotos remotos habilitados; 3 técnicos de mantenimiento (2 en taller central, 1 itinerante en campo); 1 almacenista; administración (gerente propietario, contadora y auxiliar) y 1 comercial. |
| **Áreas** | Operaciones (a cargo de Pompilio), Taller/Mantenimiento, Almacén de repuestos, Administración y Comercial. |
| **Herramientas actuales** | Excel (`ControlVuelos_ADV.xlsx` de horas y ciclos, `Mantenimientos_ADV.xlsx` del taller, kardex de repuestos del almacén), formatos en papel (orden de trabajo, checklist pre-vuelo y post-vuelo, bitácora de vuelo), plataforma/app del fabricante DJI para logs de vuelo, y WhatsApp para la coordinación diaria. No hay otro software. |
| **Clientes** | 2 ingenios azucareros (contrato anual por hectárea), asociación de arroceros del norte del Tolima, 3 haciendas de palma, agroempresas medianas de plátano y maíz, y grupos de pequeños productores. Pago por hectárea trabajada. |

*Datos fijados en la sesión inicial y mantenidos idénticos en todas las sesiones.*

---

## Preguntas y respuestas

---

## Sesión 1 — Bloques 1–3: Contexto, Operación de fumigación, Actores y roles

### Bloque 1 — Contexto de la organización y del negocio

**P1. [A] ¿A qué se dedica la empresa, cuándo se creó y cómo llegó a prestar fumigación con drones?**

«Miren: AgroDrones del Valle S.A.S. se creó en 2018. El fundador es don Hernando Villegas, el gerente propietario, ingeniero agrónomo que trabajó como veinte años en un ingenio del Valle. La empresa arrancó haciendo mapeo y fotogrametría con dos DJI Phantom para ingenios y haciendas. En 2020 compramos los dos primeros Agras T16 y pasamos a asperjar: la pandemia apuró a los ingenios, que querían menos gente en campo, y la cosa pegó. Yo entré ese mismo año; vengo de doce años en mantenimiento — maquinaria agrícola primero, y luego cinco años como jefe de taller de una empresa de fumigación con avioneta en Girardot. Los últimos seis años los tengo acá con los drones. Hoy somos diecisiete personas y doce aeronaves.»

**P2. [P] ¿Cuántos drones tiene la flota, de qué marcas y modelos, y de qué antigüedad? ¿Son todos del mismo tipo?**

«La flota son doce, todos multirotores aspersores de líquidos (no espolvoreamos granulado). Antigüedad entre uno y seis años:

| ID interno | Modelo | Año | Rol hoy |
|---|---|---|---|
| ADV-01 a ADV-05 | DJI Agras T40 | 2022 (2), 2023 (2), 2025 (1) | Los titulares: caña y lotes grandes |
| ADV-06 a ADV-09 | DJI Agras T30 | 2021 | Trabajo de campo general |
| ADV-10 y ADV-11 | DJI Agras T16 | 2020 | "Las mulas viejas": lotes pequeños, entrenamiento, donantes de repuestos |
| ADV-12 | XAG P100 Pro | 2023 | Prueba piloto; lotes pequeños y demostraciones (tanque de 50 L) |

Ojo con esto: tener dos marcas es tener dos mundos — manuales, repuestos y plataforma distintos. El XAG nos tiene a malas con eso de los repuestos. Y los T16 ya casi no consiguen piezas en el país; por eso uno de los dos es más "donante" que operador, se los digo con honestidad.»

**P3. [N] ¿Cuántas hectáreas fumigan al año, en qué regiones y para qué cultivos? ¿Cuántas horas de vuelo acumula la flota al año?**

«Del año que acaba de cerrar, más o menos quince mil hectáreas, así: caña de azúcar unas 9.500 ha en el Valle (lo grueso), arroz unas 2.500 en el norte del Tolima, palma unas 2.000 en el norte del Cauca, y plátano y maíz unas mil entre regiones. Horas de vuelo de toda la flota: unas dos mil horas al año. Un T40 en pico hace 25 a 30 horas al mes; en valle, 8 a 10. Un detalle que les sirve: las horas las registra sola la app del fabricante, pero las baterías no acumulan horas sino ciclos de carga, y esos van por aparte en la plataforma de DJI. Y para aspersión, horas de vuelo y horas de bomba casi son lo mismo, porque la bomba trabaja volando.»

**P4. [P] ¿Cómo es el calendario del negocio? ¿Hay temporadas pico y valle? ¿Cómo cambia la demanda de mantenimiento entre unas y otras?**

«Dos picos claros: marzo a mayo y septiembre a noviembre, que son las siembras de maíz y arroz después de las primeras lluvias; y ojo, la caña casi no descansa — el ingenio tiene ciclos de fertilización y maduración todo el año. El valle es diciembre a febrero: verano, poca aspersión foliar por fuera de zonas con riego. Entonces en diciembre y enero hacemos el "taller general": flota completa adentro, revisiones a fondo, cambios programados, inventario de repuestos y capacitación a los pilotos. En pleno pico el mantenimiento se vuelve cirugía: solo lo crítico, de madrugada o de noche. Y les confieso una mala práctica: a veces en pico estiramos los intervalos del fabricante "hasta que pase la campaña"... y después lo pagamos en correctivos. La disponibilidad en octubre vale oro: un dron parado ahí nos cuesta un contrato.»

**P5. [P] ¿Quiénes son los clientes y cómo contratan?**

«Cinco tipos: (1) dos ingenios azucareros con contrato anual por hectárea y meta mensual — pagan a 30–60 días y son el 60–65 % de la plata, se los anoto porque no todos los clientes pesan igual; (2) la asociación de arroceros del norte del Tolima, por campaña, dos al año; (3) tres haciendas de palma, contratos semestrales; (4) agroempresas medianas de plátano y maíz, por lote u orden de servicio; y (5) grupos de pequeños productores que contratan la jornada completa, generalmente reunidos por una asociación o la UMATA. Negocia Sandra, la comercial, y los contratos los firma don Hernando. La tarifa es dato comercial interno, no norma: entre $40.000 y $70.000 pesos la hectárea según producto, dosis, distancia y tamaño de lote; al ingenio, por volumen anual, nos vamos a la banda baja.»

**P6. [P/N] ¿Cómo gana dinero la empresa y cuánto pesa el mantenimiento en los costos?**

«La plata entra por tarifa por hectárea aplicada — facturamos contra el informe de aplicación que firma el mayordomo del lote. El agroquímico casi siempre lo pone el cliente; nosotros a veces preparamos el caldo. Estructura de costos de un año normal, a ojo de buen cubero (cifras internas aproximadas): personal ~40 %, mantenimiento y repuestos de flota incluyendo baterías ~22 %, transporte y logística ~10 %, seguros y administración ~15 %, y el resto imprevistos. La batería es el consumible más caro: una del T40 ronda los 25 a 30 millones de pesos, y la vida útil en ciclos que le pone el fabricante — del número exacto no me consta, hay que verificarlo en el manual (certeza media). Un dato que le repito al gerente: el correctivo nos cuesta dos a tres veces lo que habría costado el preventivo, en plata y en días parados. Es cifra de tablero de taller, no de contabilidad fina.»

**P7. [P] ¿Cuál es la ventaja competitiva frente a otras empresas de drones o la avioneta?**

«Contra la avioneta: lotes chicos e irregulares (de 5 a 50 hectáreas), franjas pegadas a viviendas, acequias, árboles, la vena de caña junto a la vía; no necesitamos pista; volamos bajito con gota controlada y eso reduce la deriva; y entregamos informe por lote con mapa. En lotes grandísimos y planos la avioneta todavía gana por costo puro, no voy a mentirles. Contra otras empresas de drones: taller propio y flota propia (respondemos rápido), pilotos estables que no son freelancers, y el conocimiento de los ciclos de la caña que uno no aprende en un curso. Y una debilidad honesta: dependemos de repuestos importados; eso nos golpea la promesa de rapidez.»

**P8. [P] ¿Cuáles son los mayores riesgos del negocio hoy?**

«En orden real: (1) quedarnos sin flota disponible en pico por falta de repuestos — el número uno; (2) un incidente o accidente con químico a bordo: daño a terceros, tema ambiental y póliza; (3) que la Aerocivil nos audite y los papeles no estén al día — bitácoras, mantenimiento registrado (certeza media sobre qué exactamente nos pueden exigir; hay que verificarlo en la norma); (4) perder el contrato de un ingenio por incumplir la meta de hectáreas; (5) que el conocimiento de los T40 viva solo en la cabeza de dos técnicos; (6) robo de equipos. De esos seis, cuatro se arreglan con orden y registros, no con plata — por eso estamos hablando.»

**P9. [P] ¿Cómo está organizada la empresa? ¿Dónde está ubicado el mantenimiento y de quién depende?**

«Estructura plana: don Hernando (gerente) arriba; de ahí: Operaciones y Mantenimiento que es mía — de mí cuelgan los ocho pilotos (Camilo es el líder de cuadrilla), los tres técnicos y el taller; Almacén a cargo de Nubia; Administración con Marta la contadora y un auxiliar; y Comercial con Sandra. Diecisiete personas en total. El taller está en el galpón de Palmira, pegado a la bodega: dos bahías, mesas de trabajo, banco de pruebas de motores, estantería de repuestos y una zona de baterías con sus extintores. Y un detalle que les conviene anotar: yo cargo dos sombreros — jefe de operaciones y jefe de mantenimiento a la vez. Eso a veces me queda grande.»

**P10. [P] ¿Con qué herramientas se gestionan hoy las cosas? ¿Qué funciona bien y qué no?**

«Tres Excel: `ControlVuelos_ADV.xlsx` (horas y ciclos, alimentado con las fotos que mandan los pilotos por WhatsApp — en pico lleva dos a cuatro días de atraso), `Mantenimientos_ADV.xlsx` (mi plan por dron, con colores, lo llevo yo), y el kardex de repuestos de Nubia (a veces el técnico saca una pieza y no la anota, y el stock "dice que hay" y no hay). Papel: la orden de trabajo autocopiable, los checklists de pre y post vuelo, y la bitácora de cada dron en cuaderno. Plataforma DJI para los logs de los Agras — el XAG aparte, en su propia app. Y WhatsApp, que es donde vive la empresa un poco. ¿Qué funciona? Mi Excel, porque yo lo cuido; la OT en papel, porque impone disciplina; y un tablero blanco en el taller con verde/amarillo/rojo por dron — oro puro. ¿Qué no funciona? Consolidar horas a tiempo, el stock real, buscar históricos ("¿cuándo le cambiamos la bomba al ADV-03?" son cuarenta minutos de carpetas) y armar reportes para el gerente o la aseguradora a mano. De software, nada.»

**P11. [V] Resumen en 6 líneas y correcciones.**

_Los estudiantes resumen:_ «AgroDrones del Valle (Palmira, 2018, ~17 personas) fumiga ~15.000 ha/año en Valle, Cauca y Tolima con 12 drones (5 T40, 4 T30, 2 T16, 1 XAG) para ingenios, arroceros, haciendas de palma y agroempresas, cobrando por hectárea. El negocio es estacional, con picos marzo–mayo y septiembre–noviembre. El mantenimiento depende de Operaciones y se gestiona con Excel, papel, WhatsApp y la plataforma del fabricante; cuesta ~22 % del total. La mayor preocupación es la disponibilidad de flota en temporada alta.»

_Pompilio:_ «Bien, así es. Dos correcciones. Primera: no todos los clientes pesan igual — los ingenios son el 60–65 % de los ingresos; si un ingenio se va, nos tambaleamos. Segunda: el mantenimiento no lo vean solo como costo — es lo que me garantiza disponibilidad. Cuando gasto en preventivo, lo que estoy comprando es flota lista en octubre.»

---

### Bloque 2 — Operación de fumigación (el "cliente" del mantenimiento)

**P12. [A] Describa una misión típica de fumigación, de la aceptación del servicio al regreso a bodega.**

«Se las cuento como una de arroz en el Tolima, que es lo típico. Tres días antes, Sandra confirma con el cliente: lote, producto, dosis, y se genera la orden de servicio. La víspera, yo asigno dron y piloto por el grupo de WhatsApp. El piloto alista: revisa el equipo, carga baterías, organiza los tambores con el producto y sube todo a la camioneta con los cargadores y la planta eléctrica. A las 5:00 a.m. salen piloto y ayudante. 6:30 en el lote: hablan con el mayordomo, miran viento y condiciones, delimitan el lote — vuelan el contorno con la app o cargan el polígono —, mezclan el caldo y hacen el checklist prevuelo. El dron vuela franjas en modo autónomo; el ayudante va recargando caldo y rotando baterías en los cargadores. Al terminar: informe de aplicación en la app (hectáreas, litros, mapa), firma del mayordomo, lavado del circuito con agua limpia en campo, y a empacar. En la tarde, en bodega: descarga de registros, limpieza más completa, baterías al 50–60 % si no vuelan mañana, apunte en la bitácora y foto al grupo. Al día siguiente — o dos días después, si fue jornada pesada — se pasan horas y hectáreas al Excel. Ese es el ciclo completo.»

**P13. [P] ¿Quién planea la misión, quién la vuela, quién carga el producto y quién registra el vuelo?**

«Planea la misión el piloto en campo con la app (franjas, altura, caudal), siguiendo la orden de servicio; en lotes de ingenio a veces nos pasan el polígono del lote. Vuela el piloto remoto, con su certificación al día — de eso hablamos en el bloque 3. El producto lo carga y mezcla el ayudante de campo, con EPP y supervisión del piloto. Y el registro lo hace el dron solo: la app guarda vuelos, litros, hectáreas y alarmas. Encima de eso, el piloto diligencia el "parte de vuelo" en papel y el mayordomo firma el informe. Es decir: los datos ya existen — el problema es que quedan regados en tres partes: app, papel y WhatsApp.»

**P14. [N] ¿Cuánto dura un vuelo/carga de tanque, cuántos vuelos por jornada, cuántos drones por servicio?**

«Con el T40, que es el tanque de 40 litros: a dosis de bajo volumen (10–20 litros por hectárea, lo típico) cada carga cubre 2 a 4 hectáreas. El vuelo dura 5 a 8 minutos por carga; la recarga, con batería rotada y caldo listo, 3 a 5 minutos. En una jornada de campo (7 a 10 horas) salen 40 a 60 cargas: entre 60 y 100 hectáreas reales por dron por día en lote bueno; en lotes chicos o con traslados se cae a 30–40. Horas de vuelo por dron por jornada: 4 a 6. Baterías: 4 a 6 por dron, rotando en cargadores de campo con la planta. Drones por servicio: uno en lote mediano; en siembra grande de ingenio o campaña de arroz van dos o tres juntos.»

**P15. [P] ¿Cómo se asignan los drones a los servicios? ¿Qué criterios?**

«Eso lo defino yo. Criterios: disponibilidad (¿está en taller o volando?), horas acumuladas contra el próximo servicio — si al ADV-02 le faltan cinco horas para el service de motores, no lo mando a un servicio de tres días en el Tolima —, tamaño y forma del lote (el T40 a lotes grandes y abiertos; el XAG o los T16 a lotes pequeños, quebrados o demostraciones), estado de las baterías, y el piloto "de cabecera" de cada equipo, que es una buena práctica nuestra: cada piloto cuida su dron y lo conoce. ¿Y fallamos? Claro. Una vez mandamos el ADV-04 con un motor que ya venía cascando porque "aguantaba"... y no aguantó. De esa les cuento en la pregunta del caso.»

**P16. [P] ¿Qué se hace antes y después del vuelo? ¿Qué es mantenimiento y qué es operación?**

«Prevuelo (piloto, checklist en papel): hélices con grietas o flojas, tornillería, fugas del sistema de aspersión, estado y porcentaje de baterías, sensores limpios, prueba de motores en ralentí, calibración del caudal de la bomba cada cierto número de cargas o al cambiar de producto — eso ya lo cuento como mantenimiento de primer nivel — y prueba de patrón de boquillas. Postvuelo: lavado del circuito (tanque, filtros, mangueras, boquillas), lavado exterior para quitarse el químico — la corrosión en conectores nace de no lavar —, descarga de logs, baterías al porcentaje de almacenamiento, y anotar golpes o ruidos raros en la bitácora. La frontera en teoría es clara: el piloto hace primer nivel (limpieza, inspección, apriete, cambio de hélice por un golpe); todo desmontaje, calibración mayor o cambio de componente es del técnico en taller. En la práctica, la frontera es difusa y a veces el piloto "ayuda" más de la cuenta. Mea culpa: mala práctica que quiero corregir.»

**P17. [P] ¿Qué agroquímicos manejan y cómo afectan al equipo?**

«Herbicidas, fungicidas (arroz y maíz), insecticidas, fertilizantes foliares, madurantes y urea disuelta en caña. Los efectos: la urea y los caldos con sólidos tapan filtros y boquillas y cristalizan; los cocteles dejan residuo gomoso en tanques y mangueras; los productos salinos o ácidos corroen conectores, estructura y cuerpo de bomba; las bombas se desgastan más con caldos cargados; los sellos se endurecen. Por eso el lavado post-servicio es sagrado, el cambio de filtros es frecuente, y las boquillas se revisan por caudal y patrón con probeta y cronómetro — eso es práctica interna basada en la recomendación del manual del fabricante (certeza media-alta; el procedimiento exacto está en los manuales DJI).»

**P18. [P] ¿Qué condiciones ambientales aceleran el desgaste?**

«El polvo y la ceniza de la caña prequemada — entran a los motores y rodamientos, y los motores se truncan antes de hora. El calor del Valle: las baterías y la electrónica sufren. La humedad alta permanente más químico: corrosión acelerada de conectores. El viento: más esfuerzo de motores y menos precisión de gota. Y el lavado frecuente, que es necesario, también mete humedad a los conectores si no se seca bien. Nuestros lotes están entre 900 y 1.100 metros de altura; eso no es el drama grave acá. Práctica interna: a los equipos que trabajan polvo y urea les revisamos motores y filtros más seguido que el intervalo del manual — ojo: somos más estrictos que el manual, no más laxos.»

**P19. [C] Cuéntenos de una vez que un dron no estuvo disponible cuando se necesitaba.**

«Octubre del año pasado, plena siembra. El ADV-02, un T40, hizo aterrizaje forzoso en un lote de arroz en el Tolima por falla de un motor — cayó en el propio lote con caldo a bordo, sin daño a terceros, gracias a Dios. Resultado: brazo y motor dañados, y detrás apareció corrosión en conectores que venía de tiempo atrás. ¿El repuesto? No estaba en stock: importación, tres semanas. Esa semana reprogramamos 220 hectáreas, la asociación de arroceros quedó brava, pagamos jornales extra, tapamos lotes chicos con los T16 y el XAG, y el ADV-02 parado mirando el techo del taller. Costo total del episodio, a ojo: ocho a diez millones de pesos entre correctivo, traslados y jornales. Qué cambió: stock mínimo de brazos completos y motores para T40 y T30, y una regla mía: nunca dos drones de la misma línea en taller a la vez. Y la leída del caso: la raíz era corrosión de conectores que un preventivo bien hecho habría encontrado antes.»

**P20. [V] Confirmar el flujo de la misión y el origen de los datos.**

«Sí, así es: orden de servicio → alistamiento → vuelo con recargas → informe y firmas → lavado → bodega → registro en tres canales (app, papel, WhatsApp) → consolidación en Excel. De ahí salen las horas y los ciclos que alimentan el mantenimiento. Donde se nos enreda es en la consolidación: los datos existen, pero llegan tarde y a veces incompletos.»

---

### Bloque 3 — Actores, roles y responsabilidades

**P21. [A] ¿Quiénes participan en el mantenimiento preventivo, directa o indirectamente?**

«Directos: yo (planeo, programo, apruebo y libero), los tres técnicos — Jhon Fredy y Duberney en el taller, Yeison itinerante en campo —, los ocho pilotos (primer nivel y reporte de fallas) y Nubia en repuestos. Indirectos: Sandra (ventanas de servicio), Marta (compras y pagos), don Hernando (gastos grandes), el distribuidor DJI de Cali (repuestos, cursos, boletines, garantías), un técnico electrónico externo para placas, el gestor de importaciones, la aseguradora, la Aerocivil y el ICA en lo de los químicos.»

**P22. [P] Para cada rol: ¿qué hace, qué decide, qué firma, qué registra, ante quién responde?**

| Rol | Qué hace | Qué decide | Qué firma / registra | Responde ante |
|---|---|---|---|---|
| Piloto remoto | Vuela; prevuelo/postvuelo; mantenimiento de primer nivel | No decide parar un dron: recomienda | Checklist, parte de vuelo, bitácora (ha, litros, incidentes); el vuelo lo graba la app | Jefe de Operaciones (yo) |
| Técnico de mantenimiento | Ejecuta la OT: diagnóstico, cambio, calibración, pruebas | Recomienda no liberar si ve algo; no reprograma ni compra | Firma la OT: trabajo hecho, repuestos usados, horas del dron | Jefe de Operaciones (yo) |
| Inspector / calidad-aeronavegabilidad | **No existe como cargo** (mala práctica confesada): esa revisión la hago yo en trabajos mayores | — | — | — |
| Jefe de Operaciones y Mantenimiento (yo) | Plan de mantenimiento, programa OTs, diferencia servicios | Aprueba diferimientos con límites; libera en trabajos mayores | Firma liberación y reporte al gerente | Gerencia |
| Almacenista (Nubia) | Kardex, ubicaciones, garantías pendientes | No aprueba compras | Registra entradas/salidas de repuestos | Administración / yo |
| Coordinación de servicios (Sandra) | Contrata y agenda servicios; contacto con el cliente | No decide sobre equipos | Genera orden de servicio | Gerencia |
| Gerencia (don Hernando) | Presupuesto, compras grandes, contratos | Aprueba gastos mayores | Contratos; responsable de seguridad operacional ante autoridad y aseguradora | — |
| Ayudante de campo (lo agrego yo) | Recarga caldo y baterías; primero en ver fugas o ruidos raros | Nada | Avisa al piloto | Piloto |

**P23. [P] ¿Qué certificaciones se exigen a técnicos y pilotos? ¿Quién las valida y cada cuánto vencen? ¿Y si un técnico no la tiene vigente?**

«Esto es tema normativo, así que les marco mi certeza. Pilotos: deben estar registrados/habilitados como pilotos remotos ante la Aerocivil, y la operación agrícola tiene sus propias exigencias — categorías de operación y certificado de operador para empresas; eso se maneja por la plataforma UAS Colombia (certeza **media**: la regulación de drones cambió hace poco en el país y habría que verificar en aerocivil.gov.co los reglamentos vigentes de aeronaves no tripuladas). Los cursos los dan centros de formación aceptados. Vigencias y renovaciones: no me consta el periodo exacto (certeza **baja**) — las carpetas las lleva Marta en administración. Práctica interna: actualización anual nuestra y evaluación de vuelo interna. Técnicos: hasta donde sé no existe licencia estatal de técnico de mantenimiento de drones en Colombia (certeza **media**). Lo que existe son formaciones del fabricante: mis muchachos hicieron los cursos de mantenimiento Agras del distribuidor en Cali cuando compramos los T40, y se actualizan cuando sale modelo nuevo. Yo traigo formación técnica en mantenimiento aeronáutico de mi época de avionetas. Regla interna: técnico sin el curso al día no toca garantías ni calibraciones mayores. Y en SST: capacitación anual en manipulación de químicos y baterías de litio por el SG-SST (certeza **media** sobre qué nos aplica exactamente; eso lo define el Ministerio del Trabajo y nuestro sistema de gestión).»

**P24. [P] ¿Quién autoriza liberar un dron después de una intervención? ¿Puede ser el mismo que ejecutó?**

«La OT la firma el técnico que ejecutó. La liberación al servicio: en trabajos mayores — motor, bomba, estructura, calibración mayor — la firmo yo, con vuelo de prueba de 5 a 10 minutos revisando vibraciones y temperaturas en la app. En menores — hélice, filtros — libera el mismo técnico. ¿Puede ser el mismo que ejecutó? En mayores no, porque reviso yo, que no ejecuté. Pero confieso: cuando estoy en campo, a veces el técnico libera solo, sin contraste formal. En la aviación tripulada de donde yo vengo eso no se podía: el que repara no libera. Ahí estamos flojos y lo sé.»

**P25. [P] ¿Qué terceros intervienen y qué hacen exactamente?**

«El distribuidor DJI en Cali: venta de repuestos, cursos, trámite de garantías y boletines de servicio. DJI como fabricante: manuales, firmware y la plataforma de logs. Un técnico electrónico externo de Palmira: repara placas (controladora, radio) cuando no conviene comprar nuevas — el distribuidor no repara todo. Un gestor de importaciones: trae repuestos del exterior, de dos a seis semanas según el trámite. La aseguradora: póliza de responsabilidad civil; para siniestros piden evidencia de mantenimiento (certeza **media** — es cláusula de la póliza; hay que leer el condicionado). La Aerocivil: registro de aeronaves y pilotos y operación según reglamento (certeza **media** en los detalles; verificar en fuente oficial). Y el ICA en el tema de aplicación de agroquímicos — registros más del producto que del dron (certeza **media**).»

**P26. [P] ¿Cómo se coordinan hoy estos roles (reuniones, mensajes, formatos)?**

«Reunión de planeación los lunes 6:30 a.m. — yo, Sandra, Camilo y Jhon Fredy: servicios de la semana, qué drones paran, qué repuestos hacen falta. Dos grupos de WhatsApp: "Operación ADV" y "Taller ADV" (partes de vuelo, fotos de daños, urgencias). La OT en papel autocopiable con tres copias: taller, almacén, contabilidad. El tablero blanco del taller con el estado de cada dron (verde/amarillo/rojo), actualizado a mano todos los días. Mi Excel de mantenimientos lo reviso los viernes. Y mucho se resuelve con una llamada a las nueve de la noche — funciona, pero nada queda escrito donde debiera quedar.»

**P27. [V] Confirmar la lista de roles y responsabilidades.**

«La tabla está bien. Tres matices: primero, el ayudante de campo también hace parte, aunque no sea técnico — es el primero que ve una fuga. Segundo, yo cargo dos sombreros (operaciones + mantenimiento) y la función de inspector no existe como cargo: eso es una debilidad, anótenla. Y tercero, lo que más nos duele hoy no es gente sino información: horas a tiempo, stock real e histórico de componentes.»

---

### Datos nuevos fijados en esta sesión (para consistencia futura)

- **Personas:** Gerente y fundador: don Hernando Villegas. Técnicos: Jhon Fredy y Duberney (taller), Yeison (itinerante). Almacenista: Nubia. Contadora: Marta. Comercial: Sandra. Líder de pilotos: Camilo. 17 personas en total.
- **Historia:** fundada 2018 (mapeo con Phantoms); aspersión desde 2020 con los T16. Pompilio entró en 2020.
- **Cifras internas:** ingresos 60–65 % ingenios; tarifa $40.000–$70.000 COP/ha (contrato anual de ingenio en banda baja); costos: personal ~40 %, mantenimiento+repuestos ~22 %, logística ~10 %, seguros+admin ~15 %. Correctivo = 2–3× el costo del preventivo (cifra de tablero, interna). Batería T40 ≈ $25–30 millones COP (certeza media). Flota ~2.000 h/año; T40: 2–4 ha por carga de 40 L, vuelo 5–8 min, 60–100 ha/día real, 4–6 h de vuelo por jornada, 4–6 baterías rotando.
- **Producción por cultivo:** caña ~9.500 ha, arroz ~2.500, palma ~2.000, plátano+maíz ~1.000.
- **Caso fijado:** incidente ADV-02 (T40), octubre 2025, Tolima — falla de motor por corrosión de conectores; brazo sin stock (3 semanas de importación); 220 ha reprogramadas; costo $8–10 M COP; generó stock mínimo de brazos/motores y regla de "no dos gemelos en taller".
- **Prácticas fijadas:** taller general en dic–ene; reunión de planeación lunes 6:30 a.m.; tablero blanco verde/amarillo/rojo; OT autocopiable 3 copias; piloto "de cabecera" por dron; frontera difusa piloto/técnico (mala práctica); liberación mayor la firma Pompilio con vuelo de prueba; inspector de calidad no existe como cargo.
- **Incertidumbre registrada (a contrastar con fuente oficial):** exigencias exactas de la Aerocivil hoy (reglamento UAS vigente, plataforma UAS Colombia, certificado de operador, vigencias de licencias) → consultar aerocivil.gov.co; vida útil en ciclos de la batería T40 → manual DJI; cláusulas de la póliza → condicionado de la aseguradora; alcance ICA en aplicación con drones; alcance SG-SST.

---

## Sesión 2 — Bloques 4–8: Proceso E2E, Despiece y condiciones, Repuestos, Plan y programación, Registro de horas

### Bloque 4 — Proceso de mantenimiento preventivo (E2E)

**P28. [A] ¿Cómo funciona hoy el mantenimiento preventivo, paso a paso, desde que un dron opera hasta que queda liberado y registrado?**

«Se los recorro con un service de 100 horas. El viernes reviso mi Excel con las horas consolidadas de la semana y veo que un dron está llegando al intervalo. El lunes en la reunión de las 6:30 lo meto en la semana — o lo agendo más adelante si hay servicios encima. Nubia separa los repuestos; si no hay, la orden queda en amarillo y se pide. El día de la parada, el dron entra al taller y se abre la OT en papel: dron, horas del contador, tareas a hacer. El técnico ejecuta: diagnóstico, desmonte, cambio, calibración, pruebas de banco. Luego el vuelo de prueba — en mayores — y la liberación con firma. Cierre: la OT firmada, Nubia descuenta repuestos del kardex, yo actualizo el Excel y la bitácora, Marta registra el costo. El dron vuelve al tablero en verde. Ese es el ciclo completo.»

**P29. [P] ¿Cuáles son las etapas, qué dispara el inicio de cada una y qué marca su fin?**

«Seis etapas:
1. **Detección** — la disparan: horas/ciclos llegando al intervalo (mi revisión de los viernes), un boletín del fabricante, un hallazgo de técnico o piloto, o una alarma en la plataforma. Termina cuando la tarea entra a mi lista.
2. **Programación** — la dispara mi lista del viernes; se decide en la reunión del lunes. Termina con fecha, técnico y repuestos reservados.
3. **Alistamiento** — la dispara la OT generada; Nubia aparta u ordena repuestos. Termina con la bahía lista.
4. **Ejecución** — la dispara el dron en taller el día D. Termina con el trabajo hecho y auto-verificado por el técnico.
5. **Verificación y liberación** — la dispara el "terminado" del técnico. Termina con vuelo de prueba OK y firma de liberación.
6. **Registro y cierre** — la dispara la liberación. Termina con Excel, bitácora, kardex y contabilidad actualizados. Y le digo ya: esta etapa es la que más se atrasa.»

**P30. [P] ¿Cómo se diferencia el preventivo del correctivo y del predictivo? ¿Cuánto de cada uno? [N]**

«Preventivo: el plan por horas, ciclos, calendario y condición — manual del fabricante más mis ajustes. Correctivo: lo que ya se dañó — golpes, fallas, lo que se rompió. Predictivo casi no existe; lo más parecido es que miro alarmas y errores de los logs y la salud de las baterías en la plataforma DJI, y si algo "huele raro" — errores repetidos de un motor — adelanto la intervención. Eso sí es por condición. Del año pasado, contando las OTs: **55 % preventivo, 40 % correctivo y 5 % por condición**. El 40 % me arde — en la aviación tripulada uno opera al revés. Y buena parte de ese correctivo nace de estirar intervalos en pico.»

**P31. [P] ¿Cómo se detecta que "ya le toca"? ¿Quién y con qué dato?**

«Tres fuentes. La oficial: yo, los viernes, cruzando mi Excel contra las horas consolidadas. Las otras dos: el técnico o el piloto que ve algo en el equipo (tablero en amarillo, foto al WhatsApp), y la plataforma DJI con sus alarmas y la salud de baterías. El dato que manda: horas de vuelo del dron, ciclos de la batería por ID, y las horas propias del componente si las llevo en el Excel.»

**P32. [P] ¿Cómo se programa la intervención y cómo se evita chocar con servicios comprometidos?**

«La fecha la defino yo en la reunión del lunes. Sandra trae el calendario de clientes. Reglas mías: parar en valle o entre servicios; en pico, paradas de madrugada o nocturnas; nunca dos drones de la misma línea en taller a la vez — regla que nos dejó el ADV-02; y las tareas críticas no se negocian con el calendario: si chocan, cambio el dron del servicio, no la seguridad.»

**P33. [P] ¿Qué pasa en la intervención y qué formatos se llenan?**

«En la bahía: el técnico abre la OT (papel autocopiable) con encabezado — dron, horas del contador, tipo de servicio — y la lista de tareas del plan. Ejecuta diagnóstico → desmonte → cambio → calibración (bomba con probeta y cronómetro, caudal por boquilla) → pruebas de banco (motores, vibraciones). Cierra la OT con hallazgos, repuestos usados con sus series, horas-hombre y firma. En mayores: vuelo de prueba. Además de la OT se firman la salida de repuestos en el kardex y la bitácora del dron.»

**P34. [P] ¿Cómo se verifica el trabajo y quién libera?**

«El técnico se auto-verifica con la lista. En mayores reviso yo: leo la OT, miro tornillería sellada, corro el vuelo de prueba de 5–10 minutos con la app abierta mirando vibraciones y temperatura de motores, y firmo la liberación. Sin mi firma, un dron con trabajo mayor no sale a cliente. En menores libera el mismo técnico — ya lo hablamos en la sesión pasada.»

**P35. [P] ¿Qué se registra al cerrar la intervención?**

«Fecha de inicio y fin, horas del dron al momento de la OT, componente cambiado con serie retirada y serie instalada, técnico, repuestos usados con su costo (que pasa Marta), horas-hombre, hallazgos adicionales, y a qué contador quedó el "reloj" del componente. En teoría. En la práctica la OT sí queda completa siempre — es papel con firma — pero mi Excel a veces se actualiza dos días tarde.»

**P36. [P] ¿Cómo se actualiza el "reloj" de mantenimiento tras una intervención — se reinicia o se arrastra?**

«Se reinicia el contador del COMPONENTE, no el del dron. Las horas del dron corren para siempre, como el odómetro del carro. El motor nuevo arranca su service en cero; la batería nueva arranca sus ciclos en cero — eso lo cuenta sola la plataforma por ID; la bomba nueva, su contador en mi Excel. Y si un componente USADO pasa a otro dron, su vida remanente viaja con él: eso se arrastra a mano en la OT. ¿Se pierde a veces? Se pierde. No les voy a mentir.»

**P37. [P] ¿Qué parte del proceso es más lenta, costosa o propensa a error hoy?**

«Más lenta: la consolidación de horas — 2 a 4 días de atraso en pico, y es la que decide todo. Más propensa a error: el kardex de repuestos y el arrastre de series de componentes a mano. Más costosa: esperar repuesto importado con el dron parado. Y lo más frágil de todo: el sistema depende de que YO me siente los viernes con el Excel. Si estoy tres días en el Tolima, el preventivo se congela.»

**P38. [C] Un caso reciente completo, de principio a fin, con fechas.**

«El service de 100 horas del ADV-06 (T30), agosto de este año. **Viernes 14 de agosto:** consolido horas; el ADV-06 quedó en 96 h desde el último service. **Lunes 17:** lo agendo para el miércoles; Nubia separa filtros y kit de boquillas — faltó un juego de hélices de repuesto; pedido al distribuidor de Cali, llegó el martes con mensajería. **Miércoles 19:** dron a bahía a las 7:00; Duberney abre la OT. Hallazgo: una manguera del circuito con rajadura incipiente — se cambió también; aproveché la parada, como hay que hacer. **Jueves 20:** calibración de bomba y boquillas, pruebas de banco. **Viernes 21:** vuelo de prueba a las 6:30 a.m., todo normal, firmé la liberación a las 8:00. Total: dos días y medio (tenía estimado uno — la manguera lo alargó), unos $1,2 millones en repuestos, y el dron voló el sábado sin reclamo del cliente porque se hizo entre servicios. ¿Lo imperfecto? La OT con el hallazgo quedó en la carpeta y el Excel lo actualicé el martes siguiente. Ahí está el problema de siempre.»

**P39. [V] Resumen del flujo en pasos numerados — correcciones.**

1. Vuelo → datos en tres canales (app, papel, WhatsApp). 2. Viernes: consolidación de horas en el Excel. 3. Detección de intervalo → lista. 4. Lunes 6:30: programación (fecha, técnico, repuestos). 5. OT generada; Nubia reserva/ordena. 6. Ejecución en taller (diagnóstico, cambio, calibración, pruebas). 7. Vuelo de prueba. 8. Liberación firmada. 9. Cierre: OT, kardex, bitácora, Excel, contabilidad. 10. Tablero en verde.
«Correcto. Subrayo el 2 y el 9: ahí se nos rompe la cadena — los datos entran tarde y el cierre se digita tarde.»

---

### Bloque 5 — Despiece y condiciones de mantenimiento

**P40/P41. [A/P] Despiece completo de un dron: subsistemas y componentes.**

«Les despiece el T40, nuestro caballo de batalla:

| Subsistema | Componentes |
|---|---|
| Propulsión | 4 brazos; 8 motores (dos por brazo, coaxiales); 8 hélices |
| Energía | Baterías inteligentes (pool de DB1560); cargadores de campo; adaptadores |
| Aspersión | Tanque de 40 L; bomba; mangueras; filtros; 2 boquillas de atomización; sensor de nivel |
| Navegación/control | Controlador de vuelo; GPS/RTK; IMU; radar |
| Comunicaciones | Radiocontrol; antenas; módulo de transmisión |
| Sensores/cámaras | Cámara FPV; radar de seguimiento de terreno |
| Estructura | Chasis; brazos; patas; carcasas |

A eso súmenle lo que más falla en la práctica, que son las uniones: conectores, tornillería, sellos. El enemigo número uno de esta flota no es el motor: es la corrosión en conectores por el químico y la humedad.»

**P42. [P] ¿El despiece es igual para todos los modelos?**

«No. Los Agras (T40, T30, T16) llevan motores coaxiales — dos por brazo, ocho en total; el XAG P100 Pro es un quadricóptero simple de cuatro motores, con batería y bomba propias, y hasta boquillas distintas. Las diferencias las manejamos con el manual de cada modelo, una hoja de Excel por modelo, y el curso del técnico: al XAG solo le metemos mano Jhon Fredy y yo. El T16 es despiece parecido al T30, pero las piezas ya no salen fáciles — por eso es donante.»

**P43. [P] ¿Cada componente tiene número de serie o lote? ¿Se rastrea?**

«Los "mayores" sí: motores, brazos, baterías, controlador, bomba traen serie del fabricante; la anotamos en el kardex al recibirlos y en la OT al instalarlos. Los consumibles — hélices de repuesto, filtros, boquillas — van por lote del proveedor, a lo sumo. ¿Rastreo individual real? En papel y Excel; la única pieza que la plataforma DJI nos rastrea sola, por ID, es la batería.»

**P44. [P] ¿Los componentes se mueven entre drones? ¿Cómo se registra?**

«¡Claro que se mueven! Las baterías viven en un pool — no son "de un dron": rotan entre los T40 según la jornada. Las hélices se prestan. Un motor casi nunca se mueve, salvo en los T16 donantes. ¿Registro? Baterías: la plataforma las cuenta por ID — bien — y además cada una lleva su número marcado; hélices: nadie las rastrea, son consumibles, se los digo honesto; motor: si se mueve, la OT debe quedar con las horas que traía. Ese arrastre es manual y frágil — pregunta millonaria esa para ustedes.»

**P45. [P] ¿Componentes por vida útil limitada y "a condición"?**

«Por vida útil — horas, ciclos o calendario: baterías (ciclos y salud), hélices (horas y golpes), filtros (horas y taponamiento — mixto), mangueras (calendario y condición), sellantes. "A condición": motores (vibración, holgura de eje, ruido), bomba (caudal fuera de rango), boquillas (patrón y caudal con probeta), estructura (grietas, tornillería), electrónica (errores en el log), radar y sensores. En la práctica casi todo es mixto: hay intervalo del manual Y criterio de condición encima.»

**P46. [P/N] Tabla componente → condición → umbral → tarea → repuestos.**

| Componente | Condición | Umbral que usamos (práctica interna) | Tarea | Repuestos |
|---|---|---|---|---|
| Hélices | Horas + condición | Revisión 25 h; cambio ~100 h o por golpe/griega | Inspección, cambio | Hélice + tornillos |
| Motores | Horas + condición | Inspección 100 h; cambio ~300 h o por vibración | Inspección, limpieza, cambio | Motor o brazo completo |
| Batería | Ciclos + condición | Revisión mensual; retiro ~800–1.000 ciclos o salud < 80 % | Balanceo, diagnóstico, retiro | Batería |
| Bomba | Horas + condición | Revisión 100 h; calibración en cada service; cambio por caudal | Calibración (probeta), cambio | Bomba, sellos |
| Filtros | Horas + condición | Limpieza semanal en temporada; cambio 50–100 h | Lavar, cambiar | Filtro |
| Boquillas | Condición | Prueba de patrón en cada calibración; cambio si el caudal se desvía > 10 % | Probeta, cambio | Par de boquillas |
| Mangueras | Calendario + condición | Inspección 100 h; cambio ~1 año o rajadura | Cambio | Manguera, abrazaderas |
| Estructura/tornillería | Horas + condición | Reapriete 25 h; inspección tras golpe | Inspección, torque | Tornillería, sellante |
| Controlador/ESC | Condición + calendario | Revisión con errores en log; firmware anual | Diagnóstico, actualización | — |
| GPS/RTK, radar | Condición | Limpieza; revisión si falla señal | Limpieza, calibración | — |

«Los números que usamos salen del manual del fabricante ajustados con nuestra experiencia; los exactos habría que verificarlos uno a uno contra el manual DJI/XAG vigente (certeza media). Lo que les aseguro es la LÓGICA: horas para lo mecánico, ciclos para baterías, calendario para hules y sellados, condición para electrónica y estructura.»

**P47. [P] Si hay varias condiciones, ¿cuál manda?**

«Lo que ocurra primero. La batería con 700 ciclos pero salud en 75 %: se va. La manguera de seis meses que ya está resecada: se cambia. Es norma del oficio y también viene en los manuales (certeza media-alta).»

**P48. [P] ¿Cómo se definen y cuentan los ciclos?**

«Depende del componente — apúntenlo porque ni nosotros somos consistentes en el papel. Para la BATERÍA: un ciclo de carga, contado por la plataforma DJI por ID. Para el DRON: no hablamos de ciclos — hablamos de horas de vuelo y número de vuelos. Para la BOMBA y el TANQUE: contamos cargas de caldo (llenados), que es lo que los castiga. O sea: "ciclo" en mi taller significa tres cosas distintas según de qué hablemos.»

**P49. [P] ¿Qué tolerancias hay para adelantar o diferir? ¿Quién autoriza?**

«Práctica interna, que el manual no fija (certeza media): adelantar, libre hasta un 10 % del intervalo. Diferir: tareas críticas de seguridad — motores, estructura, batería hinchada — NUNCA; el dron no vuela. Tareas menores: hasta un 10 % con mi firma. El que autoriza diferir soy yo. Y confieso: en pico se han estirado más de la cuenta — el ADV-02 empezó exactamente así.»

**P50. [P] ¿Qué pasa si la condición se vence con el dron en servicio?**

«Regla: crítico = aterriza y ya. Menor = termina la jornada y entra al taller al regreso, sin volar al día siguiente. Decide el piloto en el momento con mi criterio por teléfono, y confirmo yo. Si el servicio del cliente queda enredado, mando sustituto o reprogramo con Sandra. Lo que NO puede pasar es que una condición crítica se pase porque "no podemos perder el contrato" — esa pelea la gano yo.»

**P51. [P] ¿Cómo se maneja la vida remanente de componentes que se mueven o se reparan?**

«El contador pertenece al componente, no al dron. Batería: la plataforma lo sabe por ID — fácil. Motor o bomba usados: el arrastre de horas se escribe en la OT al desmontar y al instalar ("este motor sale del ADV-10 con 180 h") — manual y frágil; a veces la nota queda solo en la carpeta. Con los T16 donantes hemos pasado piezas con la vida contada así. Es de lo más flojo que tenemos.»

**P52. [P] ¿Qué se hace en campo y qué en taller?**

«Campo — piloto o Yeison: limpieza y lavados, inspección visual, aprietes, cambio de hélice por golpe, calibración de caudal con probeta, limpieza de filtros, firmware cuando toca. Taller — Jhon Fredy y Duberney: motores, bombas, mangueras, estructura, calibraciones mayores, diagnóstico de baterías, electrónica (o el técnico externo para placas). Regla práctica: si hay que desmontar más de una tapa, va al taller.»

**P53. [P] ¿Firmware y calibraciones periódicas son mantenimiento preventivo?**

«Sí lo cuento como preventivo — calendario. Lo maneja Yeison; el fabricante manda avisos. Regla interna: NO actualizar firmware en plena campaña salvo parche crítico — un firmware nuevo en octubre puede dejarnos un dron raro con la temporada encima. En el taller general de diciembre actualizamos toda la flota y las versiones quedan congeladas hasta el diciembre siguiente, salvo boletín crítico (certeza media: es práctica nuestra, no norma).»

**P54. [C] Ciclo de vida completo de una batería y una boquilla.**

«La batería: llega en cajón del distribuidor; Nubia la recibe contra factura y toma la serie al kardex; le pegamos su número; primeras cargas de acondicionamiento; entra al pool de los T40. Desde ahí la plataforma acumula ciclos y salud por su ID. Yeison le hace revisión mensual — balanceo, hinchazón, temperatura. Cuando llega a 800–1.000 ciclos o salud por debajo del 80 %, la bajamos: unos meses de banco de pruebas y de ahí al gestor de residuos (certeza media-baja en la parte ambiental — habría que verificar con la autoridad ambiental el posconsumo de baterías de litio). Nos dura 18–24 meses en temporada. La boquilla: llega en kit; se instala en diez minutos; en cada calibración le hacemos prueba de caudal con probeta y cronómetro; si el patrón sale chuzado o el caudal se desvía más del 10 %, se cambia. Con urera aguanta semanas en plena temporada; con fungicidas, meses. La gastada es chatarra común.»

**P55. [V] Confirmar la tabla "componente → condición → umbral → tarea → repuestos" para 5 componentes.**

«Confirmo la de P46 para hélice, motor, batería, bomba y filtro — esa es la que rige, con la salvedad de contrastar los números con el manual DJI vigente.»

---

### Bloque 6 — Repuestos y consumibles

**P56. [A] ¿Qué repuestos y consumibles necesita el preventivo?**

«Consumibles: hélices, filtros, boquillas, mangueras, tornillería, sellante, grasa, cinta. Repuestos mayores: motores, brazos completos, bombas, baterías, tanques, patas, cargadores. Y para el XAG: todo importado, que es el peor de los casos.»

**P57. [P] Repuestos por tipo de cambio y cantidades. ¿Kits?**

| Cambio | Repuestos | Cantidad | Kit |
|---|---|---|---|
| Hélice | Hélice + tornillos nuevos | 1 u 8 (se revisa el brazo completo) | DJI trae kit de hélices |
| Motor | Motor o brazo completo | 1 (y se revisa el coaxial) | Brazo completo recomendado |
| Bomba | Bomba + sellos + manguera | 1 | Kit de bomba del distribuidor |
| Filtro | Filtro | 1–2 | Kit de filtros de temporada |
| Boquilla | Par de boquillas | 2 | Kit de boquillas |
| Batería | Batería | 1 | — |

«Sí hay kits: el distribuidor nos arma un "kit de temporada" — filtros, boquillas, hélices — para el inicio de cada pico. Práctica de él que nos ha funcionado.»

**P58. [P] ¿Cómo se maneja el stock hoy?**

«Bodega del galpón, estantería marcada por modelo. Controla Nubia con el kardex en Excel; salida solo con firma contra la OT. ¿Cómo se sabe qué hay? Consultando el Excel — que se descuadra porque a veces el técnico saca algo urgente y la anotación queda debida. Conteo físico trimestral; descuadre típico del 5 al 10 %.»

**P59. [N] Stock mínimo, punto de reposición, lead times.**

«Después del ADV-02 fijamos mínimos: 2 brazos T40, 1 T30, 2 motores sueltos, 2 bombas, 8 hélices por modelo, 10 filtros, 6 boquillas, 1 batería de reserva. Reposición: se toca el mínimo → pedido inmediato. Entregas: distribuidor de Cali con existencias, 1–3 días (mismo día con mensajería si es urgente); importación, 2–6 semanas; y la aduana a veces tranca el trámite — riesgo número uno de disponibilidad.»

**P60. [P] ¿Quiénes son los proveedores y cómo es la importación?**

«El distribuidor DJI de Cali lleva el 80 % de la plata; lo que no tiene, se importa por el gestor aduanero; el técnico electrónico local repara placas; y el XAG se surte con un importador de Bogotá que demora bastante más — por eso el XAG es el último de la fila. El gestor arma los papeles de aduana; los tiempos varían y hay imprevistos.»

**P61. [P] ¿Cómo se solicita y aprueba una compra?**

«Flujo: necesidad detectada (técnico o yo) → si toca mínimo, Nubia genera solicitud → apruebo yo hasta $5 millones; por encima firma don Hernando → Marta ordena el pago → Nubia recibe, verifica contra factura y toma series. Urgencias de fin de semana: compro yo del bolsillo y me reembolsan — como en toda pyme.»

**P62. [P] ¿Cómo se trata un repuesto en garantía?**

«Reclamo al distribuidor con: serie, fecha y factura, registro de uso (de la plataforma DJI si es batería), descripción de la falla y a veces los logs. El trámite tarda semanas; mientras tanto compras el repuesto nuevo o paras el dron — el peor de los mundos. Hemos ganado reclamaciones de baterías y perdido otras por "mal uso": ahí es donde la evidencia de carga y almacenamiento de la plataforma vale plata.»

**P63. [P] ¿Qué pasa con los componentes retirados?**

«Baterías: gestor de residuos / posconsumo (certeza media-baja — habría que verificar la obligación exacta con la autoridad ambiental o el Ministerio de Ambiente). Electrónica y motores chatarra: gestor de RAEE del municipio. Piezas con vida: caja de "donantes" etiquetada. Todo queda en un cuaderno de bajas — frágil, como todo lo nuestro en papel. No me pidan número de resolución porque no me consta.»

**P64. [P] ¿Trazabilidad de serie/lote desde llegada a instalación?**

«Factura → kardex (con serie) → OT (serie retirada / serie instalada) → bitácora del dron. Todo existe… en papel y dos Excel. Cuando se hace, funciona; cuando hay urgencia, la serie se anota después — y a veces nunca.»

**P65. [P] ¿Qué pasa si falta un repuesto para la intervención?**

«La OT queda "en espera" — tablero amarillo. El dron: si el faltante es de tarea crítica, no vuela; si es menor, sigue operativo mientras llega. Mensajería urgente al distribuidor, o reprogramo el servicio con Sandra y mando sustituto. Del caso ADV-02 salió precisamente la regla del stock mínimo.»

**P66. [N] Costos aproximados de componentes y consumibles.**

| Componente | Costo aprox. (COP) |
|---|---|
| Batería T40 (DB1560) | $25–30 millones |
| Batería T30 | $18–22 millones |
| Brazo completo T40 | $8–12 millones |
| Motor | $2–3 millones |
| Bomba completa | $3–5 millones |
| Juego de 8 hélices | $1,5–2 millones |
| Manguera del circuito | $400–700 mil |
| Par de boquillas | $300–500 mil |
| Filtro | $150–250 mil |

«Precios de lista del distribuidor, aproximados — se mueven con el dólar (certeza media).»

**P67. [V] Confirmar relación tareas-repuestos-proveedores.**

«Confirmo: tareas del plan → repuestos del kardex → proveedores: Cali para DJI, Bogotá para el XAG, importación para lo que no haya.»

---

### Bloque 7 — Plan de mantenimiento y su programación

**P68. [A] ¿Cómo está estructurado el plan de mantenimiento?**

«Mi Excel `Mantenimientos_ADV.xlsx`: una hoja por modelo con las tareas y sus intervalos, y columnas por dron con la última ejecución (fecha y horas). Colores: verde al día, amarillo por vencer, rojo vencido. Más un calendario de pared con las paradas grandes del año. El "documento" de fondo es el manual del fabricante; mi Excel es la herramienta de trabajo.»

**P69. [P] ¿El plan es por modelo, por componente o por dron? ¿Quién lo define y aprueba?**

«Nace POR MODELO — del manual — y se ajusta POR DRON según su historia: al ADV-10 (donante) casi no le hago plan; a los T40 que trabajan polvo y urea les apretamos las inspecciones. Lo defino yo con los manuales y la experiencia; don Hernando lo "aprueba" viéndolo en diciembre durante el taller general — informal, pero así es.»

**P70. [P] ¿Cómo se versionan o actualizan los planes?**

«Cambian por tres cosas: boletín del fabricante, hallazgos nuestros — tras el ADV-02 metí la inspección de conectores cada 50 horas — y cambios normativos si los hubiera (certeza media). ¿Cómo se versiona? Mal: la mayoría de cambios quedan anotados en la misma hoja con fecha, y algunos solo en mi cabeza o en notas del celular. Debilidad confesa.»

**P71. [P] ¿Cómo se programan las intervenciones y cada cuánto se revisa la flota?**

«Ciclo semanal: viernes reviso el Excel contra las horas consolidadas → armo mi lista → el lunes a las 6:30 decidimos la semana con Sandra y los técnicos: paradas, técnicos, repuestos. Cada semana se re-decide. El taller general de diciembre se agenda desde octubre. El que lo hace: yo.»

**P72. [P] ¿Cómo agrupan tareas en una sola parada?**

«Siempre que se pueda: si el dron entra para una parada, se le hace TODO lo que esté por vencer en las próximas 25–50 horas — filtros, boquillas, calibración, reapriete, firmware. Una parada, todo junto. Lo contrario es tener al dron entrando y saliendo cada semana.»

**P73. [P] ¿Cómo se concilia el plan con los servicios a clientes? ¿Quién tiene prioridad?**

«Sandra trae el calendario al lunes. Prioridades: (1) tareas críticas de seguridad, (2) contrato del cliente, (3) tareas menores. Conflicto entre 1 y 2: gana la seguridad — cambio el dron del servicio o reprogramo y aviso al cliente. Menores se difieren con mi firma hasta el 10 %. La discusión sana es cuánto cuesta diferir — y a veces cuesta caro (otra vez el ADV-02).»

**P74. [P] ¿Cómo se asignan técnicos y espacio? ¿Restricciones?**

«T40 y T30: Jhon Fredy y Duberney, que tienen el curso del modelo. Yeison: campo, menores, calibraciones y firmware. El XAG: Jhon Fredy y yo. Restricción física: dos bahías — máximo dos drones en taller a la vez. Restricción de carga: en pico no puedo sacrificar un técnico tres días seguidos a una parada grande.»

**P75. [P] ¿Cómo se notifica a los involucrados y con cuánta antelación?**

«Lunes por WhatsApp a los grupos de Operación y Taller; el tablero se actualiza ese mismo día; a Nubia le queda la reserva de repuestos. Antelación: la misma semana — normalmente 2 a 4 días; paradas grandes, con una semana o más. Y a veces, lo confieso, la notificación es el piloto llegando y el dron ya no está. Eso pasa y no debería.»

**P76. [P] ¿Qué pasa cuando una intervención programada no se cumple?**

«La OT queda abierta en "pendiente" — tablero amarillo — y se re-agenda el lunes siguiente. Registro: anotación al pie de la OT con el motivo (repuesto, técnico o tiempo) y la columna de reprogramada en el Excel. A veces el motivo queda solo en la memoria de la reunión — otro punto flaco.»

**P77. [P] ¿Mantenimiento obligatorio vs. recomendado?**

«Tres capas: (1) lo que exige la autoridad aeronáutica en materia de aeronavegabilidad — condición segura y registros (certeza media sobre el detalle exacto; verificar el reglamento vigente); (2) el manual del fabricante — recomendación técnica muy fuerte, que seguimos como si fuera obligatoria; (3) nuestras prácticas internas — a veces más estrictas (polvo, urea). En mi taller: tareas de seguridad son sagradas; el resto se programa con criterio.»

**P78. [N] ¿Qué % se cumple a tiempo? ¿Duración promedio por tipo?**

«Cumplimiento a tiempo el año pasado: **65–70 %** — me da vergüenza, pero es la verdad; mi meta es 85 %. Duraciones promedio: prevuelo diario del piloto: 10–15 min; service 25 h: medio día; service 100 h: un día (con hallazgos, día y medio); cambio de bomba: medio día; service mayor de motores: 2–3 días; calibración de caudal en campo: 1–2 horas.»

**P79. [V] Ejemplo: "para el dron X con estas horas, el plan generaría…".**

«Tomen el ADV-03 (T40) con 240 horas de dron y 95 horas desde su último service de 100 h. El viernes el Excel me lo pintaría amarillo → service de 100 h: revisión completa, filtros, calibración de bomba y boquillas, reapriete, inspección de conectores. Los motores, que tienen 180 h propias, quedan para la parada de 300 h del dron salvo hallazgo. Repuestos: kit de filtros, par de boquillas, sellante. Parada: un día en bahía 1 con Duberney. Eso generaría mi plan hoy, tal cual.»

---

### Bloque 8 — Registro de horas de vuelo, ciclos y telemetría

**P80. [A] ¿Cómo se registran hoy las horas y ciclos de cada dron?**

«Tres canales: la app del fabricante (automático, en vivo), el parte de vuelo en papel del piloto (al final de la jornada) y mi consolidación semanal al Excel. Ciclos: los cuenta la plataforma por cada batería, por ID; el resto de la flota trabaja con horas y con cargas de caldo anotadas a mano.»

**P81. [P] ¿Quién registra, cuándo y con qué formato?**

«El dron registra en tiempo real, mientras haya sincronización. El piloto llena el parte al terminar la jornada — papel, lo fotografía al WhatsApp. Sandra o yo lo digitamos al Excel al día siguiente si hay tiempo; los viernes consolido yo, seguro.»

**P82. [P] ¿Qué datos exactos se capturan por vuelo?**

«De la app: fecha, dron, duración, área, litros asperjados, batería usada por ID, alarmas y errores, ruta con mapa. Del papel: piloto, lote, cliente, producto y dosis, incidentes. Del WhatsApp: todo lo demás — y nada formal. La unión de los tres es "el registro de la operación".»

**P83. [P] ¿Qué entrega la telemetría, cómo se descarga y quién la usa?**

«La plataforma entrega: horas de motor por dron, ciclos y salud por batería, voltajes, alarmas de vuelo, errores de motor/ESC, velocidad de viento y el registro de vuelos. Se descarga manual — export de la cuenta DJI; el XAG, en su propia app. No tenemos integración con nada: el fabricante tiene un servicio de gestión de flota en la nube, pero es de pago y no lo tenemos contratado (certeza media en nombre y costos exactos). La usamos yo — los viernes — y los técnicos cuando diagnostican.»

**P84. [P] ¿La información es confiable? ¿Discrepancias?**

«El dron no miente (certeza alta): lo que se sincroniza es confiable. El papel sí miente: hectáreas mal contadas, dígitos, caldos que no cuadran con litros. Regla para discrepancias: para horas de mantenimiento manda la plataforma; para facturar manda el informe firmado por el mayordomo. Las resuelvo yo, a ojo y con llamada al piloto. Y cuando el dron voló sin sincronizar, la app no sabe y el papel es lo único que hay.»

**P85. [P] ¿Qué hacen si faltan datos o están mal registrados?**

«Reconstruyo con el parte papel y la orden de servicio; llamo al piloto y al mayordomo. Si no queda, el registro queda "por confirmar" y lo cierro con lo que haya, con la incertidumbre anotada — cuando me acuerdo. La batería que voló sin registro queda con ciclos subestimados: por eso miro salud, no solo ciclos.»

**P86. [P] ¿Cómo se asignan horas y ciclos a componentes específicos?**

«La batería: sola, por ID, en la plataforma — el único caso bien hecho. Motores, bomba y demás: NO. El dron acumula horas de dron; el componente acumula lo que yo arrastre a mano en la OT y el Excel. Al cambiar un motor, la hora de corte queda escrita en la OT y su contador arranca en cero. Es el punto más frágil de todo el registro — se lo digo yo antes de que lo descubran ustedes.»

**P87. [P] ¿La telemetría viene de una plataforma del fabricante? ¿Restricciones o costos?**

«DJI: cuenta de la empresa, app del piloto y plataforma web; exportación manual; los datos viven en la nube del fabricante — hasta dónde y con qué historia podamos descargar habría que leer los términos (certeza media). La plataforma básica viene con el equipo; la gestión avanzada es de pago y no la tenemos. El XAG: otra app, otro idioma — doble trabajo.»

**P88. [N] ¿Con qué frecuencia se actualizan los acumulados? ¿Qué desfase es aceptable?**

«En vivo en la app; consolidación al Excel semanal — los viernes — que en pico se estira a 3–4 días por las jornadas. ¿Desfase aceptable para decidir? Uno o dos días. Con cuatro días se me pueden pasar intervalos — y eso pasa, no lo niego. El ideal es mismo día, pero nadie digita a las diez de la noche.»

**P89. [V] Confirmar el flujo: operación → registro → acumulado → alerta.**

«Confirmo: vuelo → registro (app + parte papel + WhatsApp) → consolidación (Excel, viernes) → detección de intervalo (mi lista) → programación (lunes) → intervención → cierre. La cadena es correcta; los eslabones débiles son la consolidación tardía y el cierre digitado a mano.»

---

### Datos nuevos fijados en la Sesión 2 (para consistencia futura)

- **Proceso E2E:** 6 etapas (detección → programación → alistamiento → ejecución → verificación/liberación → registro y cierre); disparadores y fines por etapa definidos. Mix actual: **55 % preventivo / 40 % correctivo / 5 % por condición**.
- **Intervalos internos (práctica; exactos del manual "a verificar"):** inspección 25 h (reapriete, hélices); service menor 100 h; mayor de motores ~300 h; conectores cada 50 h (nueva tras ADV-02); calibración de bomba/boquillas en cada service; filtros: limpieza semanal en temporada, cambio 50–100 h; batería: retiro ~800–1.000 ciclos o salud < 80 %, vida 18–24 meses; boquilla: cambio si caudal se desvía > 10 %; mangueras ~1 año.
- **"Ciclo" es polisémico (glosario):** batería = ciclo de carga (plataforma, por ID); dron = horas de vuelo; bomba/tanque = cargas de caldo.
- **Diferimientos:** críticas nunca se difieren (dron no vuela); menores hasta 10 % con firma de Pompilio; adelanto libre hasta 10 %.
- **Stock mínimo fijado** (2 brazos T40, 1 T30, 2 motores, 2 bombas, 8 hélices/modelo, 10 filtros, 6 boquillas, 1 batería). Lead times: Cali 1–3 días; importación 2–6 semanas. Aprobación: Pompilio ≤ $5 M COP; don Hernando > $5 M. Descuadre típico del kardex: 5–10 %; conteo trimestral. Kit de temporada del distribuidor.
- **Costos repuestos (aprox., certeza media):** batería T40 $25–30 M; T30 $18–22 M; brazo T40 $8–12 M; motor $2–3 M; bomba $3–5 M; 8 hélices $1,5–2 M; boquillas $300–500 mil el par; filtro $150–250 mil.
- **Plan:** Excel por modelo con columnas por dron; nace del manual, se ajusta por dron; aprobación informal en diciembre; cambios por boletín/hallazgo/normativa, versionado débil. Prioridades: seguridad > contrato > tareas menores. Máximo 2 bahías simultáneas.
- **Cumplimiento:** 65–70 % a tiempo; meta 85 %. Duraciones: 25 h = ½ día; 100 h = 1 día; motores = 2–3 días; calibración de campo = 1–2 h.
- **Caso fijado Sesión 2:** service 100 h del ADV-06 (T30), ago 14–21 de 2026; hallazgo de manguera; 2,5 días; ~$1,2 M COP; Excel actualizado con 4 días de retraso.
- **Registro:** 3 canales (app DJI en vivo, parte papel diario, consolidación viernes); desfase 2–4 días en pico; para mantenimiento manda la plataforma, para facturar el informe firmado; único componente con contador automático = batería (por ID); gestión de flota en la nube del fabricante NO contratada.
- **Términos de glosario surgidos (V7):** service, parada, condición, diferimiento, "tablero verde/amarillo/rojo", parte de vuelo, OT, bitácora, donante, pool de baterías, carga de caldo, kit de temporada.
- **Incertidumbre registrada:** intervalos exactos del manual DJI/XAG por componente; posconsumo de baterías de litio (autoridad ambiental / MinAmbiente); detalle de lo exigible por Aerocivil sobre mantenimiento y registros; términos de la plataforma DJI (descarga/historia de datos); servicio de gestión de flota del fabricante (nombre/costo).

---

## Sesión 3 — Bloques 9–13: Indicadores, Capacidades y recursos, Excepciones, Normatividad, Interoperabilidad

### Bloque 9 — Indicadores del proceso

**P90. [A] ¿Qué indicadores usan hoy?**

«Formales, casi ninguno — se los digo honesto. Lo que hay es mi tablero mental y el Excel. Miro tres cosas: si los drones están en verde (disponibilidad), cuántas OTs preventivas se cumplieron a tiempo, y cuánto se fue en mantenimiento contra lo presupuestado. Al gerente le entrego cada mes una hojita: disponibilidad del mes, correctivos del mes y plata gastada. Y el "cómo vamos" muchas veces es conversado, no calculado.»

**P91. [P/N] Fórmula, fuente, frecuencia, meta y responsable de cada indicador.**

| Indicador | Fórmula (como la uso) | Fuente | Frecuencia | Meta | Responsable | Valor actual |
|---|---|---|---|---|---|---|
| Disponibilidad de flota | dron-días en verde / dron-días del período × 100. "Disponible" = verde en tablero, service al día, baterías operativas. No descuento los donantes del denominador — a veces sí (inconsistencia confesa) | Tablero + Excel | Mensual (gerente); a mí me gustaría diaria | No hay número formal; informal: 90 % | Yo | ~90 % valle; 80–85 % pico |
| Cumplimiento del plan | OTs preventivas cerradas en la ventana / programadas × 100 | Mantenimientos_ADV.xlsx | Semanal yo / mensual gerente | 85 % (dicha, no escrita) | Yo | 65–70 % |
| MTBF | No lo calculamos formal. "Falla" = correctivo que saca el dron. Aproximación mía: un correctivo cada ~40 h de vuelo de flota. Debería ser por componente: hoy imposible | Conteo de OTs correctivas / horas | Cuando me acuerdo | — | Yo | ~40 h flota agregada |
| Costo mant. por hora | (repuestos + mano de obra + servicios externos) / horas de vuelo del período | Facturas (Marta) + horas (Excel) | Mensual | −15 % en dos años (conversado) | Marta / yo | ~$80–100 mil COP/h |
| Tiempo medio de reparación | entrada a taller → liberación | OTs | A ojo | — | Yo | 1–2 días con repuesto; hasta 3 semanas esperando; media ~4 días |
| Correctivo vs preventivo | proporción de OTs por tipo | OTs | Mensual | Correctivo ≤ 25 % | Yo | 55 % prev / 40 % corr / 5 % condición |
| Hallazgos por inspección | OTs que encuentran algo extra / total | OTs | — | — | Yo | ~1 de cada 3 |

**P92. [P] ¿Quién consulta cada indicador y para qué?**

«El gerente: disponibilidad y costo, mensual — decide presupuesto y presión de contratos. Yo: todos, semanal — programar paradas y compras. Marta: los costos, para contabilidad. La aseguradora: en un siniestro pide evidencia de mantenimiento. Algunos ingenios en auditoría de contrato piden registros — de qué exactamente no me consta (certeza media). Y Sandra me pregunta "¿cuántos drones puedo prometer?" — y eso se lo respondo a ojo.»

**P93. [P] ¿Qué indicador les preocupa más y qué valor tiene?**

«La disponibilidad en pico: 80–85 % cuando el negocio necesita tres drones el mismo día en tres municipios distintos. Y su hermano, el cumplimiento del plan en 65–70 %. La raíz de los dos es la misma: datos tardíos y repuestos.»

**P94. [P] ¿Qué datos les faltan para calcular bien?**

«Las horas consolidadas a tiempo (desfase de 2–4 días en pico); los acumulados por componente (el arrastre es manual, así que un MTBF por componente es imposible hoy); el stock confiable (descuadre 5–10 %); el costo por OT cerrado (Marta lo tiene por factura, no por dron); y el histórico del estado diario del tablero — el tablero se borra, no queda registro.»

**P95. [C] Ejemplo numérico de un mes real.**

«Octubre del año pasado, el mes del ADV-02. Cálculo: 12 drones × 31 días = 372 dron-días. Parados: ADV-02, 21 días (incidente + repuesto); ADV-11, 8 (esperando motor de importación); ADV-09, 5 (service mayor); ADV-10, 15 (donante, en taller "de paso"). Contando los 12: (372−49)/372 = **86,8 %**. Excluyendo el donante: (341−34)/341 = **90 %**. La cifra que le mostré al gerente fue 88 %, "a ojo de buen cubero". O sea: mismo mes, tres respuestas válidas según cómo se cuente. Un sistema tendría que obligarnos a definir UNA sola.»

**P96. [V] Confirmación de fórmulas.**

«Sí, esas son las fórmulas como las uso… o como DEBERÍA usarlas, porque la de disponibilidad la acabo de formalizar hablando con ustedes. Anótenlo.»

### Bloque 10 — Capacidades y recursos del negocio

**P97. [A] ¿Qué funciones debe tener una empresa como la suya, de punta a punta?**

«Diez, a mi manera de ver: (1) vender y atender clientes; (2) programar y planificar los servicios; (3) operar el vuelo y la aspersión; (4) gestionar la flota y su mantenimiento; (5) gestionar repuestos, compras e importaciones; (6) gestionar el talento: pilotos, técnicos y sus certificaciones; (7) cumplir la norma aeronáutica, agrícola, ambiental y de SST; (8) administrar las finanzas y los costos; (9) informar: al cliente, a la autoridad, a la aseguradora; (10) seguridad operacional y manejo de incidentes.»

**P98. [P] Para cada una: qué sabe hacer, quién la realiza, con qué recursos.**

| Función | Qué sabe hacer | Quién | Recursos |
|---|---|---|---|
| Vender/atender clientes | Prospectar, contratar, tratar con mayordomos | Sandra + don Hernando | Contratos, referencias |
| Programar servicios | Calendarizar lotes, equipos y cuadrillas | Sandra conmigo | Excel de servicios, WhatsApp |
| Operar vuelo/aspersión | Volar, mezclar, aplicar, informar | 8 pilotos + ayudantes | Flota, baterías, camionetas, EPP |
| Flota y mantenimiento | Prevenir, corregir, liberar | Yo + 3 técnicos | Taller, banco de pruebas, manuales, plan |
| Repuestos/compras | Stock, importar, garantías | Nubia + Marta + yo | Kardex, proveedores, gestor aduanero |
| Talento | Contratar, formar, certificar | Marta | Carpetas, cursos del distribuidor |
| Cumplimiento | Registros, licencias, renovaciones | Marta + don Hernando + yo | Carpetas, plataforma UAS |
| Finanzas | Facturar, costos, presupuesto | Marta + don Hernando | Contabilidad, facturas |
| Informar | Informes de aplicación, evidencias | Pilotos + Sandra | Plataforma DJI, partes firmados |
| Seguridad/incidentes | Prevenir, responder, investigar | Yo (SST con Marta) | Protocolos, póliza, capacitaciones |

**P99. [P] ¿Cuáles son el corazón, cuáles estratégicas, cuáles de apoyo?**

«Corazón — si fallan no hay negocio: operación de vuelo, mantenimiento y disponibilidad de flota, y la programación fina. Estratégicas: la relación con los ingenios, el cumplimiento normativo (nos habilita a operar) y el conocimiento agronómico. Apoyo: compras, finanzas, talento, y TI — que hoy es inexistente.»

**P100. [P] ¿Qué tan maduras son? ¿Cuáles tercerizadas?**

«Fuertes: la operación (pilotos estables) y el taller técnico (gente muy buena, aunque poca). Informales: la gestión de registros y datos, el cumplimiento (carpetas de Marta "más o menos" al día) y las compras (funcionan a pulso). Débiles: indicadores, gestión del conocimiento — todo vive en cabezas — y TI. Tercerizadas: la auditoría contable externa anual, el gestor aduanero, la reparación de placas, el posconsumo de residuos y las capacitaciones del distribuidor.»

**P101. [P] Recursos tangibles e intangibles críticos.**

«Tangibles: la flota (12), el pool de unas 30 baterías con sus cargadores, el banco de pruebas, el galpón con sus dos bahías, tres camionetas con plantas eléctricas, herramientas especializadas y el stock de repuestos. Intangibles: los registros y bitácoras (la aeronavegabilidad demostrable), licencias y certificados vigentes, los contratos con los ingenios, el conocimiento de los técnicos — eso no se compra — y la reputación con los mayordomos.»

**P102. [P] ¿Qué funciones se ven afectadas por buen o mal preventivo?**

«Casi todas: la operación (disponibilidad diaria), la comercial (qué puede prometer Sandra), las finanzas (el correctivo cuesta 2–3 veces), el cumplimiento (aeronavegabilidad y póliza) y la seguridad — una falla en vuelo con químico a bordo es lo que me quita el sueño.»

**P103. [P] ¿Qué funciones dependen de información de mantenimiento?**

«Programación de servicios: necesita disponibilidad y horas remanentes. Compras: necesita lo que se va a vencer — el kit de temporada se calcula con el plan. Finanzas: costos por dron. Calidad y seguridad: incidentes y hallazgos. Comercial: capacidad vendible. Autoridad y aseguradora: evidencias.»

**P104. [V] Validación de la lista.**

«Completa. Yo agregaría una transversal: "mantener el orden" — los registros al día. Hoy esa función la hacemos a medias entre Marta, Nubia y yo, y es justo la que queremos sistematizar.»

### Bloque 11 — Excepciones y situaciones difíciles

**P105. [A] Situaciones fuera de lo normal que más complican.**

«Repuesto que no llega cuando toca; condición que vence en plena campaña; falla en campo; técnico clave enfermo o de curso vencido; boletín del fabricante que cambia un intervalo; datos de horas que no cuadran; y el incidente con químico a bordo, que gracias a Dios solo ha pasado una vez.»

**P106. [P] ¿Qué hacen cuando…?**

- **Un dron falla en campo:** el piloto aterriza. Si es menor — hélice, taponamiento — lo corrige en el sitio y sigue. Si es mayor: baja el equipo, avisa, va Yeison o se trae al taller; al cliente, sustituto o reprogramación. Queda OT correctiva.
- **Se vence una condición con el dron comprometido:** ya lo hablamos: crítico aterriza y no vuela; menor termina la jornada y entra al taller. Lo autorizo yo.
- **No hay repuesto y la importación tarda:** canibalizo donantes (los T16), pido prestado entre gemelos, compro el brazo completo (más caro pero más rápido) o reprogramo servicios. El caso ADV-02 quedó registrado.
- **El técnico certificado no está:** espera, o lo hace el otro certificado. El XAG sin Jhon Fredy no se toca. Mala práctica confesa: una calibración menor la ha hecho un técnico sin el curso del modelo, con supervisión mía por teléfono — no me enorgullece.
- **Hay accidente o incidente:** asegurar la zona, verificar terceros, aviso inmediato a don Hernando y a la aseguradora, evaluar si hay reporte ante la Aerocivil según el protocolo vigente (certeza media — verificar el RAC 100 y el reporte de ocurrencias de la UAEAC), investigación interna, OT correctiva, y cambio de procedimiento si aplica.
- **Falla prematura de componente:** garantía si aplica (con la evidencia de la plataforma), análisis de causa — ¿por qué se dañó antes? —, ajustar intervalo o proveedor, y registrar como hallazgo.
- **Dos drones necesitan el mismo repuesto:** prioridad al servicio más crítico (contrato con multa), canibalizo donante, compra urgente.
- **Dato de horas erróneo o faltante:** reconstruyo con papel y llamadas; si la diferencia es grande — 20 horas, digamos — el dron entra a revisión antes de volver a volar; nota correctiva en el Excel.
- **Boletín del fabricante cambia un intervalo:** llega por correo del distribuidor; lo leo, evalúo cuánta flota queda vencida con el intervalo nuevo, armo campaña especial inmediata, y actualizo el Excel — el versionado, ya les confesé, es débil.
- **Componente vuelve de garantía o reparación externa:** llegada con serie, vida remanente, prueba antes de instalar, y OT con el arrastre escrito.

**P107. [P] ¿Quién decide en cada caso?**

«Casi todo lo decido yo. Los siniestros, con don Hernando y la aseguradora. Las compras grandes, don Hernando. El resto del tiempo: yo, con el teléfono en la mano.»

**P108. [P] ¿Cómo se registra la excepción?**

«OT correctiva con nota al margen cuando se hace bien; a veces solo en la memoria de la reunión del lunes cuando se hace mal. Débil, lo reconozco.»

**P109. [C] El peor incidente de mantenimiento que han vivido.**

«El ADV-02 ya se los conté. El otro que me marcó: 2024, el ADV-07 (T30) perdió presión de bomba en pleno vuelo sobre arroz — quedó una franja mal aplicada y tuvimos que REHACER 12 hectáreas gratis. Causa: filtro con sedimento de urera y una boquilla obstruida. Qué cambiamos: malla de colado del caldo obligatoria en campo y frecuencia de cambio de filtro. Costo: las 12 ha rehechas y unos $600 mil en repuestos. Ese día el mayordomo me dijo: "ustedes me responden con la franja mal aplicada o me responden con papeles". Preferí los papeles, y ha sido mejor.»

**P110. [V] Excepciones más frecuentes.**

«Confirmo: la más frecuente es el repuesto faltante, y la segunda, el estiramiento de condiciones en plena temporada. Las dos me las firmo yo.»

### Bloque 12 — Normatividad y cumplimiento (Colombia)

> Nota del entrevistador: todas las respuestas con nivel de certeza. Contrastar con fuente oficial antes de usar (aerocivil.gov.co, ica.gov.co, mintrabajo.gov.co, minambiente.gov.co).

**P111. [A] ¿Qué normas y autoridades regulan la operación y el mantenimiento?**

«Les digo las que conozco y manejo, con mi certeza: la **Aerocivil (UAEAC)** — autoridad aeronáutica; la reglamentación de drones cambió hace poco: el **RAC 100**, reglamento de operación de sistemas de aeronaves no tripuladas, con su plataforma "UAS Colombia" (certeza **media** — del número y fecha exactos de la resolución asociada no me consta; verificar en aerocivil.gov.co). El **ICA** en lo de plaguicidas y aplicación. El **MinSalud**: Decreto 1843 de 1991 sobre uso y manejo de plaguicidas (certeza **media**; es anterior a los drones — cómo nos aplica exactamente, verificarlo con el ICA). **MinTrabajo**: SST. **MinAmbiente** y las corporaciones autónomas regionales — acá la CVC, Cortolima y la CRC — en residuos. Y la **Ley 1581 de 2012** de datos personales (certeza **alta**, esa la conozco bien).»

**P112. [P] ¿Qué le exige la autoridad aeronáutica a un operador agrícola?**

«Por lo que manejamos (certeza **media**, verificar en el RAC 100): registro de cada aeronave en la plataforma UAS Colombia — todos los nuestros están registrados; certificado de piloto UAS / idoneidad según la categoría de operación — mis 8 pilotos; registro o certificado de **operador** para la empresa; la operación agrícola entra en las categorías con requisitos adicionales; y seguro de responsabilidad civil según la operación (certeza **media**). Documento a consultar: el RAC 100 y la resolución asociada, en la página de la Aerocivil.»

**P113. [P] ¿Qué exige la norma específicamente sobre mantenimiento?**

«Me consta la exigencia de mantener la aeronave en condición segura y llevar registros (certeza **media**). No me consta que la norma fije intervalos por componente — eso viene del fabricante. Dónde queda exactamente la línea, habría que leerlo en el capítulo respectivo del reglamento. Sugerencia: pregunta concreta al distribuidor o a la Aerocivil.»

**P114. [P] ¿Qué registros deben llevar, por cuánto tiempo y quién los audita?**

«Llevamos: bitácoras de vuelo por dron (cuaderno), bitácoras de mantenimiento (OTs archivadas), licencias y registros al día. ¿Cuánto tiempo guardarlos? No me consta el plazo exacto (certeza **baja**) — en aviación general se habla de años; verificar en el reglamento. Nos auditarían: la Aerocivil en una inspección, la aseguradora en un siniestro, y los ingenios en auditorías comerciales — eso sí nos ha pasado.»

**P115. [P] ¿Qué reportes deben entregar a la autoridad?**

«Reporte rutinario mensual no hay que yo sepa (certeza **media**). Lo que sí existe: reporte de incidentes/accidentes según el protocolo de ocurrencias de la UAEAC (certeza **media** — verificar el procedimiento vigente), y las renovaciones y trámites por la plataforma UAS Colombia.»

**P116. [P] ¿Consecuencias de incumplir?**

«Sanciones del reglamento — multas, suspensión de la operación — y efectos en la póliza si hay siniestro sin mantenimiento demostrable (certeza **media**). No les cito cifras porque no me constan.»

**P117. [P] ¿Requisitos de técnicos y pilotos?**

«Pilotos: certificado de piloto UAS, cursos en centros aceptados, y lo que pida la categoría agrícola (certeza **media**; vigencias exactas: certeza **baja** — las carpetas las lleva Marta). Examen médico ocupacional lo manejamos por SST (práctica interna). Técnicos: hasta donde sé no hay licencia estatal de técnico de mantenimiento de drones (certeza **media**) — lo que hay son cursos del fabricante/distribuidor. Todos: capacitación anual SST.»

**P118. [P] ¿Normas de aspersión de agroquímicos con drones?**

«El ICA: productos registrados, dosis de etiqueta. La aplicación aérea de plaguicidas está regulada desde el Decreto 1843 de 1991 — que es de la Ley 9 de 1979, muy anterior a los drones (certeza **media** que nos aplique tal cual; verificar con el ICA cómo tratanan la aspersión con UAS). La relación con mantenimiento: la calibración de caudal y boquillas es lo que garantiza la dosis — por eso la probeta y el cronómetro. Y hojas de seguridad de cada producto, siempre.»

**P119. [P] ¿Normas ambientales que afectan el mantenimiento?**

«Envases de plaguicidas: posconsumo con devolución al comercializador — Resolución 1675 de 2013 creo (certeza **media**); los devolvemos en el agroinsumo. Baterías: posconsumo de pilas y acumuladores — Resolución 1297 de 2010 (certeza **media**) — y salió regulación nueva de baterías usadas hace poco (2025) cuyo alcance a las de litio no conozco (certeza **media-baja**; verificar en MinAmbiente). Nosotros entregamos con gestor y guardamos los certificados de disposición. El caldo sobrante y agua de lavado: se aplica en el mismo lote o se devuelve — jamás a fuentes de agua (práctica interna + sentido común sanitario). Chatarra electrónica: gestor de RAEE.»

**P120. [P] ¿SST en taller y con baterías/químicos?**

«SG-SST del Decreto 1072 de 2015 con los estándares de la Resolución 0312 de 2019 (certeza **media-alta** — verificar en MinTrabajo qué nos aplica por tamaño). EPP, hojas de seguridad, extintores — en la zona de baterías los apropiados —, señalética y capacitación anual.»

**P121. [P] ¿Qué exigen las aseguradoras?**

«Póliza de responsabilidad civil para operar (certeza **media** de que es exigible según la operación). Y en siniestros piden evidencia de mantenimiento — es cláusula del condicionado; hay que leerlo (certeza **media**). La póliza la maneja Marta con don Hernando.»

**P122. [P] ¿Protección de datos personales?**

«Ley 1581 de 2012 (certeza **alta**). Nuestras bases: clientes, pilotos y técnicos en Excel. Tratamiento de datos interno, sin registro de bases ante la SIC hasta donde sé — probablemente deberíamos revisarlo (certeza **media**; consultar la SIC).»

**P123. [P] ¿Qué parte del manual del fabricante es obligatoria?**

«Distinción en tres capas: la autoridad exige condición segura — y el manual del fabricante es la referencia técnica para demostrarla (certeza **media**). Dentro del manual: las advertencias y secciones de seguridad son sagradas; el resto es recomendación del fabricante. Y nuestras prácticas internas pueden ser más estrictas que el manual — nunca más laxas.»

**P124. [P] ¿Cambios normativos recientes que les afecten?**

«El cambio grande es la nueva reglamentación UAS — el RAC 100 con la plataforma nueva y el certificado de idoneidad (certeza **media**; nos enteramos por boletín del distribuidor). Para nosotros lo relevante es qué exige a operadores agrícolas en mantenimiento y registros. Tarea pendiente: leerla completa con el distribuidor.»

**P125. [N] ¿Plazos o límites numéricos que conozca?**

«Honesto: no me constan los números — ni plazos de retención de registros ni vigencias exactas de licencias (certeza **baja**). Lo que manejamos operativamente: póliza anual, capacitación SST anual, licencias al día en las carpetas. Los números exactos: verificarlos en las fuentes oficiales, no en mi memoria.»

**P126. [P] Para cada obligación, ¿qué evidencia se debe poder mostrar?**

| Obligación | Evidencia |
|---|---|
| Registro de aeronaves | Certificado/registro en plataforma UAS Colombia |
| Pilotos habilitados | Certificados vigentes (carpetas de Marta) |
| Vuelo y mantenimiento | Bitácoras de vuelo y OTs archivadas |
| Aplicación | Informe de aplicación firmado por el mayordomo |
| Seguro | Póliza vigente |
| SST | Certificados de capacitación, exámenes |
| Químicos | Hojas de seguridad, etiquetas/dosis |
| Residuos | Certificados de disposición del gestor |

**P127. [V] "Usted nos dice que [X] aplica: ¿es norma, práctica del fabricante o criterio interno?"**

«Queda así: intervalos por componente = fabricante (recomendación técnica). Condición segura, registros, licencias = norma (aeronáutica). "Lo que ocurra primero", conectores cada 50 h, malla de colado, congelar firmware en campaña = criterio interno nuestro. Y las tres capas se suman: nunca restan.»

### Bloque 13 — Interoperabilidad

**P128. [P] Con la programación de servicios (Sandra).**

«Sale de mantenimiento hacia ella: disponibilidad por dron (verde/amarillo/rojo), fechas de parada programadas, horas que le quedan a cada equipo, y mi "no prometas más de X drones esta semana". Llega de ella: el calendario de servicios — lote, hectáreas, fechas, horas estimadas. Quién inicia: la reunión del lunes 6:30 y WhatsApp diario en pico; los conflictos, por teléfono. Formato: su Excel de servicios y WhatsApp. Dueños: ella de los servicios, yo de la disponibilidad. Calidad: fechas buena; horas estimadas con ±20 %. Si falla: dron prometido y no disponible → sustituto o reprogramación y cliente molesto — ha pasado. Y apúntense esta: para Sandra "disponible" significa "el dron existe y hay piloto"; para mí significa "verde con service al día". Mismo vocablo, dos verdades — para el piloto además el servicio se llama "misión" y en la oficina "servicio". Frecuencia: diaria en pico; 15 a 25 servicios al mes.»

**P129. [P] Con inventario y compras (Nubia).**

«Sale del taller: requerimiento por OT, consumos reales, y lo que se vence pronto — el kit de temporada se calcula con mi plan. Llega: existencias, ubicación en estantería, reservas, tiempos de entrega. Inicia: la OT programada (reserva) o el mínimo tocado (compra). Formato: kardex en Excel y vales de salida en papel; lo urgente por WhatsApp. Dueña: Nubia; aprobar compras: yo hasta $5 millones, don Hernando arriba. Calidad: descuadre del 5–10 %. Si falla: OT en amarillo esperando repuesto — el clásico. Términos: para Nubia "salida" es el movimiento del kardex; para el taller "consumo" es lo que se gastó — y no siempre coinciden, porque hay salidas que se anotan tarde. Y "stock" para ella son las unidades en bodega; para mí es "lo que puedo usar hoy", sin contar lo reservado. Frecuencia: diaria; 10–20 movimientos por semana.»

**P130. [P] Con la telemetría de los drones.**

«Datos que entrega: horas de motor por dron, ciclos y salud por batería (por ID), voltajes, alarmas, errores de motor/ESC, rutas y litros. Dirección: llega — la descargamos nosotros. Quién inicia: yo los viernes o el técnico al diagnosticar; nada automático. Formato: plataforma web/app del fabricante, exportación manual de archivos. Dueño: la cuenta DJI de la empresa — pero el dato vive en la nube de ellos; hasta dónde podemos descargar y con qué historia, hay que leer los términos (certeza media). Calidad: alta cuando sincroniza; huecos sin señal en campo. Si falla: papel y memoria. Términos: DJI habla de "registro de vuelo" y "horas de motor"; nosotros decimos "horas de vuelo" — casi lo mismo pero no: el motor encendido en pruebas también suma. Y el XAG es otra app con otros nombres — doble traducción. Frecuencia: consulta semanal; volúmenes grandes en pico.»

**P131. [P] Con los técnicos certificados.**

«Sale de mantenimiento: tareas realizadas y firmadas en la OT, horas-hombre, y necesidades de formación. Llega: certificaciones vigentes con sus vencimientos, y disponibilidad de los técnicos. Inicia: yo al asignar una OT; Marta al renovar cursos. Formato: carpetas físicas y PDFs en el correo; hoja de vida en Word. Dueña: Marta — débil, los vencimientos se detectan tarde (un curso vencido lo supimos al azar). Si falla: la tarea espera, o la mala práctica de la supervisión telefónica que ya confesé. Términos: "certificado" del curso del fabricante no es el "certificado/licencia" del piloto ante la Aerocivil — mismo vocablo, papeles distintos; y "habilitado" en mi taller = curso del modelo al día. Quién emite: el distribuidor/fabricante para técnicos; la Aerocivil para pilotos.»

**P132. [P] Con la autoridad aeronáutica.**

«Sale hacia ellos: registros y renovaciones por la plataforma UAS Colombia, reportes de ocurrencias si aplican (certeza media), y atención de inspecciones. Llega de ellos: certificados y registros, requisitos, y la reglamentación — el RAC 100 y sus anexos. Inicia: nosotros (trámites) o ellos (inspección/evento). Formato: plataforma en línea, oficios, correo. Dueño de los papeles: Marta; responsable legal: don Hernando. Calidad: "más o menos" al día — certeza media. Si falla: riesgo de sanción o suspensión (certeza media). Términos: para la autoridad el "registro/matrícula" es oficial; nuestro "ADV-01" es identificación interna — ¡ni se les ocurra mostrarle a un inspector el tablero como si fuera el registro! Y su "bitácora" oficial no es igual a mi cuaderno. Frecuencia: renovaciones y trámites anuales, más lo que surja.»

**P133. [P] Otros interlocutores (confirmar, ampliar o descartar).**

«Confirmo casi todos los de su lista: **Financiero/contable** (Marta): costos por OT y factura, activos — los drones van con depreciación a 5 años según ella (certeza media) — y facturación por hectárea contra el informe firmado. **Fabricante/distribuidor**: boletines de servicio, garantías, soporte, firmware y cursos; llega por correo y visitas, sale compras y reclamos. **Aseguradora**: póliza anual; en siniestro, evidencias (OTs, bitácoras). **Talento humano** (Marta): contratos, cursos, exámenes médicos ocupacionales de los pilotos. **SST/ambiental**: capacitador anual y gestor de residuos que entrega certificados de disposición. **Clientes**: los ingenios piden informes mensuales con mapas de aplicación; algunos, evidencias de operación (certeza media de qué exactamente). **Autoridad agrícola/ambiental**: el posconsumo — envases al agroinsumo, baterías al gestor. **Planeación agronómica/GIS del ingenio**: nos pasan los polígonos de los lotes por correo, y devolvemos los mapas de aplicación. Y uno que ustedes no listaron: **el clima** — ventanas de viento por estaciones del ingenio y apps; informal, por WhatsApp, pero decide si se vuela o no.»

**P134. [A] ¿Con qué otros procesos o entidades se intercambia información que no hayamos mencionado?**

«El contador externo que audita al año; la ubicación de las cuadrillas por el GPS del teléfono para la logística; y… la nube del fabricante de la que ya hablamos. Eso es todo, creo.»

---

## Sesión 4 — Bloques 14–16: Motivación, Alcance, Cierre

### Bloque 14 — Motivación y estrategia

**P135. [A] ¿Quiénes son los interesados en que el mantenimiento funcione bien?**

«Don Hernando (dueño: rentabilidad y riesgo); yo (disponibilidad y orden); los pilotos (equipos confiables y seguros); los técnicos (carga razonable, información para trabajar); los clientes e ingenios (cumplimiento y trazabilidad); la Aerocivil (cumplimiento); la aseguradora (riesgo); y las 17 familias que comemos de esto.»

**P136. [A] ¿Qué fuerzas los empujan a mejorar?**

«Cinco: la flota creció de 8 a 12 en cuatro años y el método de libreta ya no da abasto; la reglamentación nueva aprieta por registros; los correctivos suben con la flota envejeciendo; el riesgo de perder un contrato por indisponibilidad — un ingenio no espera; y la competencia: están llegando empresas más ordenadas.»

**P137. [P] ¿Qué auditorías, incidentes o indicadores los preocupan?**

«El incidente ADV-02 ($8–10 millones); el cumplimiento del plan en 65–70 %; el descuadre del kardex de 5–10 %; y una auditoría de un ingenio que nos pidió histórico de mantenimiento por dron — nos tardamos días armándolo a mano de carpetas. Ese día me dio vergüenza.»

**P138. [N] Metas con número y fecha (las que le pedí al gerente para este proyecto).**

«Disponibilidad de flota ≥ 92 % sostenida en plena temporada para 2027. Cumplimiento del plan ≥ 85 % desde el segundo semestre de 2027. Correctivo ≤ 25 % de las OTs hacia 2028. Consolidación de horas el mismo día, desde el primer mes de uso. Costo de mantenimiento por hora −15 % hacia 2028.»

**P139. [P] ¿Cómo se vería el resultado concreto?**

«Poder prometerle a Sandra tres drones con certeza; no madrugar a rezar por un motor; pasar una auditoría sin sudar; e irme de vacaciones tres días sin que el preventivo se congele.»

**P140. [P] ¿Qué principios guían sus decisiones de mantenimiento?**

«Seguridad antes que productividad: lo crítico no se difiere jamás. "Si no está escrito, no pasó". El que ejecuta no libera — aún lo incumplimos, pero es el norte. Y: los datos del fabricante son la base, nuestra experiencia va encima — nunca por debajo.»

**P141. [P] Requerimientos al software, priorizados.**

«Imprescindibles: horas y ciclos consolidados el mismo día; plan por dron con alertas de vencimiento; la OT digital con repuestos y cierre; el stock con reserva para intervenciones. Deseables: indicadores automáticos; reportes exportables para auditoría y aseguradora; y el mapa de aplicación vinculado al dron.»

**P142. [P] ¿Limitaciones?**

«Presupuesto de pyme — ojo, esto es un proyecto de universidad y no podemos pagar licencias caras por usuario; gente sin tiempo para digitar dos veces lo mismo; conectividad regular en el campo — datos móviles; todo en español y MUY fácil; y el dato del fabricante hay que exportarlo manual porque no pagamos integración.»

**P143. [P] ¿Qué pasa si no se hace nada?**

«El próximo incidente puede ser con daño a terceros y ahí sí entra la póliza y el escándalo; la flota envejece y el correctivo sube solo; la norma nueva nos puede agarrrar desordenados; y una competencia más ordenada nos gana los contratos de los ingenios.»

**P144. [P] ¿Quién decide, aprueba y se opone?**

«Decide don Hernando conmigo; la plata la aprueba él; y se oponen — suavemente — los pilotos viejos que odian digitar, y yo mismo con mis costumbres. La resistencia al cambio aquí se llama "siempre lo hemos hecho así".»

**P145. [V] Tabla interesado → impulsor → meta, confirmada.**

«Confirmada tal cual.»

### Bloque 15 — Alcance: qué entra y qué no

**P146. [A] ¿Qué incluyen exactamente en "mantenimiento preventivo"?**

«Registro y consolidación de horas y ciclos; el plan con sus condiciones por componente; la programación de OTs; la ejecución y cierre de la OT con repuestos; la liberación del dron; y los indicadores de mantenimiento. NO incluye: la misión de vuelo en sí, la facturación, la nómina, la contabilidad ni el CRM.»

**P147. [P] ¿Y el correctivo?**

«Lo gestionamos nosotros — mismos técnicos, misma OT pero marcada "C". Mi opinión: debería quedar DENTRO del registro, porque una OT es una OT y el histórico completo necesita las dos. Pero el enfoque del sistema es el preventivo. Esa decisión es de ustedes.»

**P148. [P] ¿Quién es dueño hoy de cada proceso vecino?**

«Programación de servicios: Sandra. Inventario y compras: Nubia con Marta y don Hernando. Telemetría: el fabricante, con nuestra cuenta. Personal certificado: Marta. Reporte a la autoridad: Marta con don Hernando. Mantenimiento: mío. El software me sirve A MÍ, pero necesita datos de otros cuatro — por eso les conté todo el intercambio.»

**P149. [P] De las 5 funciones deseadas, ¿cuál es la más urgente?**

«En orden: 1) horas y ciclos a tiempo — la base de todo; 2) plan y condiciones por componente; 3) OT con repuestos; 4) alertas y programación; 5) indicadores. Lo que más urge: que las horas estén al día. Lo que puede esperar: los indicadores bonitos.»

**P150. [P] ¿Qué decisiones apoyaría el software y cuáles siguen humanas?**

«Apoya: cuándo entra un dron, qué repuestos apartar, a qué técnico asigno, qué vence. Siguen siendo mías: si se difiere algo, la prioridad del cliente, y comprar. La decisión de VOLAR o NO VOLAR es de personas, siempre.»

**P151. [P] ¿Quiénes serían los usuarios?**

«Yo (uso diario fuerte); los técnicos (la OT); Nubia (stock y reservas); Sandra (disponibilidad para prometer); don Hernando (tablero mensual); quizá los pilotos desde el celular (parte de vuelo) y Marta (costos).»

**P152. [P] ¿Qué funciones ya están resueltas y no deben duplicarse?**

«Facturación y contabilidad (Marta), programación comercial (Sandra y su Excel), telemetría (la del fabricante), nómina. No me inventen un ERP — necesito el taller en orden.»

**P153. [P] ¿Qué flota y tipos de condición cubriría?**

«TODA la flota — los 12, incluidos los donantes: si no, el histórico queda cojo. Y los cuatro tipos de condición: horas, ciclos, calendario y estado.»

**P154. [P] ¿Qué sería una solución exitosa a un año?**

«Cero condiciones críticas vencidas volando; horas al día siempre; una auditoría entregada en un día; y disponibilidad ≥ 92 % en plena temporada.»

**P155. [P] ¿Qué NO esperan que haga el software?**

«Planear vuelos o misiones, facturar, nómina, contabilidad, el inventario de toda la empresa (solo repuestos de mantenimiento), ni comprar automáticamente.»

**P156. [V] Dentro / fuera / por definir.**

«DENTRO: horas y ciclos, plan y condiciones, OTs con repuestos, liberación, indicadores de mantenimiento, stock de repuestos del taller. FUERA: misiones, facturación, nómina, contabilidad, telemetría (se consume, no se construye), programación comercial (se consume). POR DEFINIR — deciden ustedes con estos hechos: el correctivo (yo digo incluirlo), compras (solo hasta la solicitud), y certificaciones de personal (yo diría que sí, para saber quién puede hacer qué).»

### Bloque 16 — Cierre y validación

**P157. [V] Recapitulación general.**

«Así es como les resumiría yo: empresa de Palmira, 17 personas, 12 drones, tres regiones, quince mil hectáreas. El mantenimiento es mío, con tres técnicos, y funciona a pulso, papel, Excel y WhatsApp. El negocio es estacional y el orden se pierde justo cuando más se necesita. Todo el conocimiento de "cuándo le toca a qué" vive en mi Excel y en mi cabeza. Los dolores: horas tardías, repuestos, históricos imposibles, y ninguna evidencia rápida para auditorías. Correcto así.»

**P158. [P] ¿Qué no preguntaron y debieron preguntar?**

«Tres cosas. El lavado y la limpieza como tarea de mantenimiento diaria — es la mitad del desgaste de esta flota y solo hablamos de componentes. La logística de baterías en campo: el cuello real de la operación no es el dron, es tener 6 baterías ciclando con planta eléctrica a las 7 de la mañana. Y la sucesión: ¿qué pasa con todo esto el día que Jhon Fredy se vaya? Esa pregunta me la hago yo también.»

**P159. [P] ¿Qué documentos podría compartir?**

«La OT en blanco (formato), el checklist de prevuelo, el formato del parte de vuelo, un export de muestra de la plataforma DJI, una hoja del Excel de mantenimientos con una fila por dron — sin datos sensibles —, el condicionado de la póliza (se lo pido a Marta) y un informe de aplicación de muestra.»

**P160. [P] ¿Errores comunes de equipos que intentan sistematizar esto?**

«Cinco, que yo he vivido o visto: creer que el software ordena lo que la gente no hace — si el técnico no firma, no hay sistema; pedir digitar tres veces lo mismo; ignorar el campo — sin señal no hay dato, y el dato nace en un lodo a 40 grados; empezar por los reportes bonitos y no por las horas al día; y no definir quién libera un dron.»

**P161. [P] ¿Qué es lo primero que le pediría a este software?**

«Que el viernes no tenga que consolidar nada: que las horas estén ahí solas, y que me avise qué dron entra al taller la próxima semana. Eso. El resto es lujo.»

**P162. [V] Resumen final de supuestos e inciertos.**

«Seguro: flota, personal, proceso, cifras internas y prácticas — eso lo viví yo. A verificar con fuentes: los intervalos exactos del manual DJI/XAG; los números y alcances del RAC 100 y su resolución; plazos de retención de registros; cláusulas exactas de la póliza; cómo aplica el Decreto 1843 de 1991 a la aspersión con drones; alcance del posconsumo de baterías de litio (1297 de 2010 y la regulación nueva de 2025); y los términos de la plataforma DJI. Todo lo demás: tómelo como lo dije, con el nivel de certeza marcado.»

---

## Sesión 5 — Bloque 17: Verificación de consistencia (repreguntas)

**P163. ¿Cuántos drones tiene y de qué modelos?**
«Doce: cinco T40 (ADV-01 a 05), cuatro T30 (ADV-06 a 09), dos T16 del 2020 (ADV-10 y 11, los donantes) y un XAG P100 Pro (ADV-12). Antigüedad de uno a seis años.» *(Consistente con Sesión 1.)*

**P164. ¿Cada cuánto se cambia un componente?**
«Hélice: revisión 25 h, cambio a ~100 h o por golpe. Motor: inspección 100 h, cambio ~300 h o por vibración. Batería: ~800–1.000 ciclos o salud < 80 %. Filtro: 50–100 h o taponamiento. Boquilla: por caudal desviado > 10 %. Del manual exacto: a verificar; esto es lo que regimos en el taller.» *(Consistente con Sesión 2, P46/P49.)*

**P165. ¿Quién libera un dron después de mantenimiento?**
«El técnico firma la OT; en trabajos mayores libero yo con vuelo de prueba de 5–10 minutos; en menores libera el mismo técnico. Inspector dedicado: no existe — esa revisión la hago yo.» *(Consistente con Sesiones 1 y 2.)*

**P166. ¿Cómo se calcula la disponibilidad de la flota?**
«Dron-días en verde sobre dron-días del período. El problema es que el denominador lo cuento distinto según el día — con o sin donantes. Actual: ~90 % en valle, 80–85 % en pico; el mes del ADV-02 dio 86,8–90 % según cómo se cuente.» *(Consistente con Sesión 3, P95.)*

**P167. ¿Cuántos técnicos certificados hay y qué certificaciones?**
«Tres: Jhon Fredy y Duberney en taller, Yeison itinerante. La "certificación" es el curso del distribuidor DJI por modelo — de licencia estatal no me consta (certeza media). Sin curso al día no tocan garantías ni calibraciones mayores.» *(Consistente con Sesiones 1 y 3.)*

**P168. ¿Qué pasa si se vence una condición con el dron comprometido?**
«Crítico: aterriza y no vuela — no se difiere. Menor: termina la jornada y entra al taller al regreso. Lo autorizo yo, y al cliente se le manda sustituto o se reprograma.» *(Consistente con Sesión 2, P50.)*

*Verificación del equipo: las seis repreguntas coinciden con las respuestas originales. Sin contradicciones detectadas.*

---

### Datos nuevos fijados en las Sesiones 3–5 (para consistencia futura)

- **Indicadores y fórmulas** (con valores actuales): disponibilidad = dron-días verdes / dron-días ×100 (~90 % valle, 80–85 % pico; meta formal: ≥92 % pico 2027); cumplimiento del plan 65–70 % (meta ≥85 % desde 2S-2027); MTBF ≈ un correctivo cada 40 h de flota (no se calcula formal); costo mant. ≈ $80–100 mil COP/h (meta −15 % a 2028); TMR 1–2 días con repuesto / hasta 3 semanas sin él; mix 55/40/5; hallazgos 1 de cada 3 OTs.
- **Metas V1 (fijadas):** disponibilidad ≥92 % en pico 2027; plan ≥85 % 2S-2027; correctivo ≤25 % de OTs a 2028; horas consolidadas el mismo día desde el mes 1; costo/hora −15 % a 2028.
- **Segundo caso fijado:** ADV-07 (T30), 2024 — pérdida de presión de bomba por filtro/boquilla con sedimento de urera; 12 ha rehechas gratis; ~$600 mil COP; generó malla de colado obligatoria.
- **Capacidades/recursos (hechos):** 10 funciones listadas; recursos tangibles: pool ~30 baterías, 3 camionetas, banco de pruebas, 2 bahías. Tercerizados: auditoría externa, gestor aduanero, placas, posconsumo, capacitaciones.
- **Normativa (certezas marcadas; TODO a contrastar):** Aerocivil — RAC 100 + plataforma UAS Colombia + certificado de operador/piloto UAS (media); resolución asociada posiblemente 1983 (baja-media). Plaguicidas — Decreto 1843 de 1991 (Ley 9/1979), aplicación a drones por verificar con ICA (media). Envases — Res. 1675 de 2013 (media). Pilas/baterías — Res. 1297 de 2010 + regulación nueva 2025 alcance litio por verificar (media-baja). SST — Decreto 1072/2015 + Res. 0312/2019 (media-alta). Datos — Ley 1581/2012 (alta). Póliza RC exigible (media).
- **Interoperabilidad / homónimos de glosario (V7):** "disponible" (Sandra vs. Pompilio); "servicio" vs "misión"; "salida" vs "consumo"; "stock" (bodega vs. usable hoy); "certificado" (curso fabricante vs. licencia Aerocivil); "registro/matrícula" (oficial vs. ADV-xx interno); "horas de motor" vs "horas de vuelo"; "bitácora" (oficial vs. cuaderno). Interlocutores confirmados: Sandra (Excel servicios + WhatsApp, lunes 6:30), Nubia (kardex + vales), DJI/XAG (export manual, cuenta empresa), Marta (carpetas certificaciones), Aerocivil (UAS Colombia), más financieros, distribuidor, aseguradora, talento, SST/ambiental, clientes (informes con mapas), GIS ingenio (polígonos/shapefiles), clima, contador externo, GPS de cuadrillas.
- **Alcance (posición del experto):** dentro: horas/ciclos, plan/condiciones, OT+repuestos+liberación, indicadores, stock del taller; fuera: misiones, facturación, nómina, contabilidad, telemetría (solo se consume), programación comercial (se consume); por definir (decisión del equipo): correctivo (experto: incluir), compras (hasta solicitud), certificaciones de personal (experto: sí). Usuarios: Pompilio, técnicos, Nubia, Sandra, gerente, quizá pilotos y Marta.
- **Requerimientos priorizados (V1):** imprescindible: horas/ciclos mismo día, alertas de plan, OT digital con repuestos, stock con reserva; deseable: indicadores automáticos, reportes exportables, mapa vinculado. Restricciones: presupuesto pyme, sin doble digitación, conectividad campo, español/fácil, export manual del fabricante.
- **Documentos que puede compartir:** OT en blanco, checklist, parte de vuelo, export DJI de muestra, hoja del Excel, condicionado de póliza, informe de aplicación.
- **Lo no preguntado que el experto destacó:** lavado como mantenimiento diario; logística de baterías en campo; sucesión del conocimiento técnico.
