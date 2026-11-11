# ArchiForge — del ArchiMate al software, con el arquitecto decidiendo

Tú eres el arquitecto: **decides** lenguaje, base de datos, arquitectura interna, estilo de servicio y patrones.
ArchiForge **aconseja** (según el modelo ArchiMate) y **ejecuta con fidelidad a tus decisiones**, verificándolas con puertas automáticas.

## ArchiForge Studio (TUI) — la forma cómoda
```
uv venv .studio-venv
uv pip install --python .studio-venv/bin/python -r requirements.txt
.studio-venv/bin/python -m forge studio
```
(En Arch no uses `pip` global: el Python del sistema es «externally managed». Sin `uv`: `python -m venv .studio-venv && .studio-venv/bin/pip install -r requirements.txt`.
Si copias comandos a zsh, quita los comentarios `#` de la misma línea: zsh interactivo no los acepta.)
Sin escribir archivos de configuración: **Nuevo proyecto** (eliges tu `.archimate` y la TUI te dice al instante qué entiende de él),
**Dominios** (decides lenguaje, arquitectura, BD y patrones con las recomendaciones al lado), **Agente y tokens** (motor `opencode`/`claude`/propio,
modelo y tokens de API), **Construir** (progreso por etapa y log en vivo) y **Ensamblar**. Teclas: `n` nuevo · `Enter` abrir/decidir · `b` construir ·
`a` ensamblar · `g` agente y tokens · `Esc` volver · `Ctrl+Q` salir.
- Los tokens se guardan en `~/.config/archiforge/credentials.json` (permisos 600), **fuera del proyecto y de git**, y llegan al agente solo por variables de entorno.
- Cada proyecto vive en `projects/<nombre>/` (su `forge.toml` lo genera la TUI); el proyecto actual del repo se importa solo la primera vez.
- Límite honesto: un `.archimate` ajeno solo sirve si sigue las convenciones de modelado de ArchiForge (agregados con rol Raíz, «Dominio: …», comandos y
  eventos). La TUI lo comprueba y explica qué falta; desacoplar el generador de este modelo concreto es trabajo pendiente.

## Flujo por comandos (3 pasos por dominio)
1. **Diseñar** (conversación con el agente): en Claude Code `/forge-design "Intervenciones"`; en OpenCode igual.
   El agente corre `forge advise`, te explica qué patrones conviene usar (y cuáles no, para no sobreingenierizar), te pregunta y guarda `decisiones/<dominio>.toml`.
   Sin agente: `python -m forge advise "X"` y luego `python -m forge decide "X" --lang java --arch hexagonal --style soa --db postgresql --patterns cqrs,memento,!state --why lenguaje="…"`. También puedes editar el TOML a mano.
2. **Construir**: `/forge "Intervenciones"` (modo agente nativo) o `python -m forge build "Intervenciones"` (el pipeline lanza al agente). No para hasta terminar y verificar; reintenta y reanuda solo.
3. **Ensamblar**: `python -m forge assemble` une los dominios construidos (compose, gateway, shell de microfrontends) y corre el humo completo.

Opciones: lenguaje `csharp|python|java` · arquitectura `clean-ddd|hexagonal` · estilo `microservicio|soa|monolito-modular` · BD `mongodb|postgresql` ·
patrones del catálogo `catalog/patrones.toml` (cqrs, pipeline, memento, state, specification, outbox, eventos, acl, cache, cifrado).
Lo que la evaluación exige (caché, memento, cifrado) es **obligatorio** por defecto (`[quality] enforce_evaluation = false` lo rebaja a aviso).

## En paralelo / varias personas
Cada dominio tiene su estado (`.forge/<dominio>/`), su plataforma de humo aislada y commits acotados a sus carpetas. Dos formas:
- Misma máquina: `python -m forge build A B C --jobs 3`.
- Cada quien en su casa: clonen el repo, cada uno decide y construye **su** dominio (`decisiones/<dominio>.toml` distinto), hace push; después se unen y corren `forge assemble`.
  El contrato del bus se genera igual para todos desde el ArchiMate, así que los servicios encajan.

## Comandos
`doctor` · `domains` (qué contextos hay, cuáles decididos y su avance) · `advise` · `decide` · `check` · `build` · `assemble` · `publish` · `status|report|render -d X` ·
modo nativo: `bootstrap|next|gate|prepare -d X` · `install-agents` (agentes `forge-*` y comandos `/forge`, `/forge-design` para Claude Code y OpenCode).
Config: `forge.toml` (`[quality] skip = ["smoke","frontend"]` omite docker/frontend; `[output] repo` clona/publica el repo del producto;
`[agent] engine = "opencode"` + `model = "proveedor/modelo"` fijan el motor y el modelo; `opencode_agent` es el agente por defecto y el pipeline usa el `forge-*` de cada etapa).

## Cómo se verifica
Conformidad ≥ 90 % con el ArchiMate (símbolo en la capa correcta), reglas de dependencia por lenguaje (`arch_csproj`, `arch_python`, `arch_java`), build/pruebas
(`dotnet test`, `pytest`, `mvn test`), ADR que cubre cada patrón elegido citando clases reales, humo con docker, build del microfrontend y revisión independiente.

## Límites honestos (leer)
- Probado: manifiesto para los 3 lenguajes × 2 arquitecturas × 3 estilos, renderizado de órdenes, y el pipeline completo con un **agente simulado** (Python hexagonal, 100 %). 25 pruebas herméticas.
- Probado en vivo: agentes y comandos de **OpenCode V2** (`opencode run --agent forge-*`, modelo `opencode/deepseek-v4.1-flash-free`) y la invocación exacta del pipeline (sin `--dir`, con `--auto` y `--agent`).
- **No probado**: .NET real, docker real, Java de extremo a extremo (sí sus puertas con muestras mínimas) y una corrida completa de un dominio con agente real.
- Contextos sin agregados (Evidencia y Reportes, Notificaciones) no sirven como dominios construidos; se simulan.
- Los archivos `decisiones/*.toml` incluidos son **borradores de ejemplo**: confírmalos o cámbialos.
- Tests: `python -m pytest tests`. Dry-run: `python -m forge -c forge.dryrun.toml decide … && … build …`.
