# ArchiForge: todo lo que el arquitecto deba decidir se decide en la TUI
Objetivo: que ninguna tecnología o forma de despliegue que no sale del modelo ArchiMate vaya fija en el generador.
Rama: main (sin commit/push hasta que se pida) · Runner: `archiforge/.venv/bin/python -m pytest archiforge/tests`

## Specs
- S1. "todo lo que el arquitecto deba decidir debe de estar en el TUI, ya que bro, esto no se tuvo en cuenta, y si no es porque reviso, todo se iba a mandar igual para todos": cada decisión de tecnología/forma de despliegue se toma en la TUI (y por CLI), sin preselección; si falta y el modelo la necesita, la herramienta se detiene y lista las opciones.
- S2. "Todos!" (sobre el inventario: frontend, despliegue, simuladores, cifrado, imágenes base).
- S3. Ya hechas antes (mismo mecanismo `decisiones/plataforma.toml`): canal de eventos (`rabbitmq`|`memoria`) y gateway (`nginx`|`propio`).
- A1 (supuesto): solo se ofrecen opciones realmente implementadas. Las que no existen (Angular, Kubernetes) no se listan; añadir una opción es añadirla al diccionario y a su generador.
- A2 (supuesto): las versiones de imagen son configuración con valor fijado por la herramienta (visible y editable), no una elección entre tecnologías.
- A3 (supuesto): el algoritmo de cifrado es decisión **por dominio** (detalle del patrón `cifrado`), no de plataforma.

## Tasks
- [x] T1 (S1,S2) Frontend: `microfrontends` | `ninguno` (solo API) — inline
- [x] T2 (S1,S2) Despliegue: `docker-compose` | `propio` (sin artefactos de despliegue) — inline
- [x] T3 (S1,S2) Simuladores: `generar` | `ninguno` (las URL de los proveedores las pone el equipo) — inline
- [x] T4 (S1,S2) Imágenes base: versiones configurables (mongo, postgres, rabbitmq, nginx, python, node) — inline
- [x] T5 (S1,S2) Algoritmo de cifrado por dominio: `aes-256-gcm` | `chacha20-poly1305` — inline
- [x] T6 (S1) TUI y CLI para todo lo anterior + documentación — inline

## Log
- L1 (2026-11-11) "Todos!" — respuesta al inventario de lo que sigue fijo en el generador.
- L0 contexto: previo, el canal de eventos y el gateway ya son decisiones de plataforma (commits 811debc, 3cac3e3).
- Ruta: todo inline (cambios acoplados en decisions/scaffold/TUI; sin unidades independientes).
- T1-T6 verificadas: 202 pruebas en verde (archiforge/tests). Con las decisiones de este repo el generador reproduce byte a byte nginx.conf, event-bus/*, simuladores e init-postgres.sql de entrega-v3.
- Decisiones de plataforma: mensajeria, gateway, frontend, despliegue, simuladores (decisiones/plataforma.toml) + [imagenes]; por dominio: patrón cifrado → algoritmo. TUI: pantalla Plataforma (tecla p) y formulario de decisiones del dominio; CLI: forge platform y forge decide --detail.
- Sin hacer (A1): Angular y Kubernetes no se ofrecen porque no hay generador para ellos; las imágenes de los Dockerfile de servicios C#/Java las escribe el agente, no el generador.
- Risk: item 3 (forge assemble/build exigen decisiones nuevas; cambia la firma de write_platform y build_manifest) y item 5 (docker-compose/Dockerfile generados). Sin verificador independiente: el usuario rechazó subagentes; cubierto por pruebas y por la regeneración idéntica.
