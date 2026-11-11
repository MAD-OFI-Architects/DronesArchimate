# Fase 4 · Criterios de diseño y preguntas de tensión

Reglas aplicadas: un agregado es un límite de consistencia transaccional; se diseña pequeño; un agregado referencia a otro solo por ID; entre agregados hay consistencia eventual vía eventos; una transacción modifica un solo agregado; la raíz es el único punto de acceso.

## ¿Dron y Componente instalado forman un agregado o son dos? (D-07)
**Dos: Dron y Componente.** La invariante que obliga a modificar juntos es «una pieza por posición y una pieza instalada en un solo dron»; vive en el Dron (con su mapa de instalación). El contador y la vida remanente pertenecen al Componente (H-20) y no exigen modificar el dron. Si un componente se mueve entre drones (pool de baterías, donantes) se tocan dos drones en dos transacciones y el componente conserva su historia; si fuera un solo agregado, cada vuelo modificaría la flota completa y la vida remanente quedaría ligada al dron. La consistencia entre ambos es eventual: el evento «Componente instalado en dron» dispara «Registrar hora de corte» en el Componente.

## ¿La Condición de mantenimiento vive dentro del componente, del plan o es su propio agregado? (D-08)
**Dentro del Plan por modelo**, como objeto de valor de la Tarea de plan (con su umbral y su fuente). Razón: cambia con boletines y hallazgos, no con cada vuelo; versionarla por modelo evita tocar cada componente. El Componente solo calcula su vida remanente a partir del umbral informado (núcleo compartido Flota-Plan, V8).

## ¿Plan de mantenimiento y Orden de trabajo son el mismo ciclo de vida o dos? (D-09)
**Dos.** El plan vive años y cambia por versiones; la OT vive días y se cierra de forma inmutable. Además hay un tercer agregado, el Programa semanal, porque las restricciones de capacidad (dos bahías, misma línea) solo se pueden proteger viendo todas las paradas de la semana.

## ¿El registro de horas debe poder crecer sin límite dentro de otro agregado? (D-10)
**No.** Se acota por Jornada de vuelo (un dron, un piloto, un día) y la telemetría importada por archivo (idempotente). Así el tamaño es limitado y la concurrencia se reduce a la jornada.

## ¿Qué cambia si el consumo de repuestos se confirma después (eventual)? (D-11)
La **reserva** es inmediata y fuerte dentro de Existencia (no se promete lo que no hay), pero el **consumo** se confirma por el evento «Orden de trabajo cerrada». Consecuencia aceptada: durante unos minutos la existencia puede mostrar lo reservado como no consumido; el kardex externo ya se descuadra hoy por anotaciones tardías (5-10 %), por lo que la reserva inmediata mejora el estado actual.

## Revisión cruzada (paso 7): intentar romper cada invariante
- *Dos técnicos cierran la misma OT a la vez:* la OT es un solo agregado; el segundo cierre falla por «OT cerrada inmutable».
- *El jefe libera un trabajo que él ejecutó:* falla «quien ejecuta no libera»; en campo el técnico no puede liberar mayores.
- *Se instala un motor en dos drones:* el estado del componente (instalado) impide la segunda instalación; la política compensa si hubo carrera.
- *Se programan tres paradas en la misma semana:* el Programa semanal rechaza la tercera (dos bahías).
- *Un archivo de telemetría se importa dos veces:* la huella lo rechaza (idempotencia).
