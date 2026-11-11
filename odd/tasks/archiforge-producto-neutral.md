# ArchiForge como producto: sin sugerencias, el arquitecto elige todo
Objetivo: que el generador y la TUI no recomienden, preseleccionen ni citen la evaluación/rúbrica/profesor; todo lo decide el arquitecto.
Rama: main (commits por slice, sin push salvo orden) · Runner: `archiforge/.venv/bin/python -m pytest archiforge/tests`

## Specs
- S1. "La idea es que no se sugiera nada, solo que uno sea el que elija cual usar, nada de recomendaciones": sin etiquetas «recomendado/opcional/no necesario», sin patrones ni lenguaje/arquitectura/estilo/BD preseleccionados, sin «la herramienta aconseja/recomienda».
- S2. "nada de el profe lo dice en la rubrica, debe ser como si fuera un producto final": ni en la TUI, ni en mensajes, ni en prompts, README, gates o agentes aparecen «evaluación», «rúbrica», «profesor/profe». Lo que antes eran requisitos de la evaluación pasa a ser una **política del proyecto** opcional y neutral (`[policy]` en forge.toml), apagada por defecto.
- S3. Previo (L2, 2026-11-11): "porque solo hay esos patrones deberían ser todos los que existen" → el catálogo se ampliará después (fase 2) sobre este catálogo neutral: descripciones informativas, sin veredictos.
- A1 (supuesto): las descripciones «qué es / cuándo se usa / cuándo no / costo» de cada patrón son documentación de referencia, no recomendación; se muestran sin juicio sobre el dominio elegido.
- A2 (supuesto): `forge advise` se elimina (era la recomendación); se sustituye por `forge patterns` (catálogo informativo).
- A3 (supuesto): el forge.toml de este repositorio conserva las reglas que ya tenía el equipo, ahora declaradas como `[policy]` (se quitan borrando la sección).

## Tasks
- [x] T1 (S1,S2) Núcleo: `[policy]` (config, decisions.validate, gates), catálogo sin `evaluacion`, `advisor` → solo hechos del modelo, CLI (`patterns`, sin `advise`), prompts, agentes, scaffold, README — inline
- [x] T2 (S1,S2) TUI: decisión sin preselección ni etiquetas, detalle sin «recomienda», panel de políticas solo si existen, copy neutral — inline
- [x] T3 (S2) Mover los documentos de la rúbrica fuera de la herramienta y revisar que no quede el vocabulario — inline

## Log
- L1 (2026-11-11) "La idea es que no se sugiera nada, solo que uno sea el que elija cual usar, nada de recomendaciones, y nada de el profe lo dice en la rubrica, debe ser como si fuera un producto final"
- L0 contexto: la fase 1 (interconexión síncrona) quedó en 69a9ac2; las fases del libro de patrones y prompts por decisión siguen después de esto.
- Ruta: todo inline (cambios acoplados, sin unidades independientes).
- Risk T1: item 3 (se elimina el subcomando `advise` y la clave `quality.enforce_evaluation`; contratos del CLI/config propios del proyecto). Sin verificador independiente: el usuario rechazó subagentes; se cubre con pruebas.
- T1-T3 verificadas: 99 pruebas en verde. Barrido de vocabulario (evaluación/rúbrica/profe/recomend/aconsej/sugier) sobre forge/, prompts/, catálogo, README y agentes generados: solo quedan las instrucciones de NO sugerir. Capturas: formulario en blanco, referencia sin veredictos, panel de políticas solo si hay [policy].
- Rúbrica movida a docs/curso/ (fuera de la herramienta). forge.toml del repo declara el [policy] que el equipo ya tenía.
- Pendiente: fase 2 (libro de patrones completo) y fase 3 (guías por decisión en los prompts) sobre este catálogo neutral.
