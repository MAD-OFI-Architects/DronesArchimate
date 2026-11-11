# TUI de ArchiForge
Objetivo: convertir el flujo por comandos/archivos de ArchiForge en una TUI (Textual) bonita, sin que el usuario edite configuración.
Rama: main (commits por slice, sin push) · Estrategia de entrega: ask-on-risk · Runner de pruebas: `pytest archiforge/tests` (venv en el scratchpad)

## Specs
- S1. "convertir esto en una TUI para que sea mas practico" / "que yo no tenga que hacer archivos de configuracion": todo el flujo (proyecto, decisiones, construir, ensamblar) se hace desde pantallas; la TUI escribe `forge.toml` y `decisiones/*.toml` por el usuario.
- S2. "que tenga la posibilidad de hacerlo con cualquier archivo de archimate": se elige el `.archimate` (y opcionalmente la carpeta de documentos) desde la TUI; si el modelo no trae lo que el generador espera, la TUI lo dice con claridad en vez de fallar con un traceback. (El desacople total del generador respecto de este modelo es trabajo posterior: supuesto A1.)
- S3. "que quede bien bonita": diseño cuidado (tema, tarjetas, tabla de dominios con estado, progreso por etapa, atajos visibles).
- S4. "que yo tenga la posibilidad de escoger el modelo, el agente, o las API tokens": pantalla de agente con motor (claude/opencode/custom), modelo y agente de OpenCode, y tokens de API. Los tokens NO se guardan en el proyecto ni en git, no se imprimen ni van a logs: se guardan en el directorio de configuración del usuario con permisos 600 y se pasan solo por entorno al proceso del agente.
- S5. La lógica vive fuera de Textual (servicios probables sin UI) y la TUI es solo presentación: se reutilizan `decisions`, `advisor`, `Runner`, `cmd_assemble`, sin reescribirlas. El CLI actual sigue funcionando igual.
- A1 (supuesto): primero la TUI sobre el modelo actual; el generador genérico para cualquier ArchiMate va después.

## Tasks
- [x] T1 (S4,S5) Credenciales y entorno del agente (`forge/credentials.py`, env en `agents.run_agent`/`Runner`) — inline
- [x] T2 (S1,S2,S5) Proyectos: modelo, registro, `forge.toml` generado, `tool_root` separado de la raíz del proyecto — inline
- [x] T3 (S1,S5) Servicio de estudio sin UI: dominios+estado, advise, guardar decisión, construir con callbacks de log, ensamblar — inline
- [ ] T4 (S1,S3,S4) App Textual: pantallas Proyecto, Dominios, Decisión, Agente/Tokens, Construcción, Ensamblado — inline
- [ ] T5 (S3) Verificación headless con el pilot de Textual y revisión visual; README y `forge studio` como comando

## Log
- L1 (2026-11-11) "Hagamos entonces la TUI que quede bien bonita por favor"
- L2 (2026-11-11) "que yo tenga la posibilidad de escoger el modelo, el agente, o las API tokens"
- L0 contexto: pregunta previa "antes de hacer la TUI…" y "que tenga la posibilidad de hacerlo con cualquier archivo de archimate".
- Ruta: todo inline; ninguna condición de escritor delegado (unidades secuenciales y dependientes).
- T1-T3 verificadas: 63 pruebas en verde (antes 34). Bug cazado por prueba: el borrador proponía `pipeline` sin `cqrs`; ahora arrastra dependencias.
- Risk T1: item 2 (credenciales). Verificación: revisión propia (sin verificador independiente: el usuario rechazó subagentes); comprobado a mano que el token no aparece en argv, cabecera del log ni errores; permisos 600/700 con prueba.
- Risk T2/T3: item 3 leve (Config.docs_dir ahora opcional, Runner/build_one con parámetros opcionales; el CLI no cambia).
