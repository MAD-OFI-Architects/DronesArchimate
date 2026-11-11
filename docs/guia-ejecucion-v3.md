# Guía de ejecución de ArchiForge — Evaluación V3

## Objetivo

Se construyeron dos dominios reales:

- **Intervenciones**: C#, Clean Architecture + DDD, MongoDB, Claude Code.
- **Repuestos del Taller**: Python, arquitectura hexagonal, PostgreSQL, OpenCode/Claude Code.

Los demás contextos del modelo ArchiMate se emulan para demostrar interoperabilidad.

## 1. Origen de los datos ArchiMate

El modelo ArchiMate **ya estaba en el proyecto** antes de iniciar esta ejecución. No se creó ni se extrajo desde la presentación.

La configuración existente apuntaba a:

```toml
[inputs]
archimate = "inputs/DronesArchimate/modelo/drones-mantenimiento.archimate"
docs_dir = "inputs/DronesArchimate"
reference_guide = "reference/guia_ddd.md"
```

La presentación `Evaluación Final.pptx` se usó como fuente de los requisitos de la evaluación, no como fuente del modelo.

## 2. Cuándo se leyó ArchiMate

Se leyó en la primera etapa de cada build:

```text
S00-ir — Extraer el modelo ArchiMate a IR
```

ArchiForge lee el archivo `.archimate`, consulta `docs_dir` y construye una representación intermedia —IR— con contextos, agregados, comandos, eventos, políticas, contratos y relaciones.

En esta ejecución el IR reportó:

```text
9 contextos · 13 agregados · 54 comandos · 59 eventos · 24 políticas · 37 contratos
```

Después, `S01-manifest` derivó los símbolos que cada dominio debía implementar.

## 3. Relación entre V1, V2 y V3

La V3 se trató como acumulativa:

```text
V1 = automatización desde ArchiMate
V2 = automatización + capas externas e interoperabilidad
V3 = V1 + V2 + cliente web con microfrontends
```

Por eso no se hicieron tres sistemas separados. Al completar V3 también se cubren los requisitos acumulados de V1 y V2.

## 4. Preparación

```bash
cd /home/dishyma/repos/archiforge
.venv/bin/python -m forge doctor
```

Se verificaron Git, Python, Node/npm, Docker, Docker Compose, .NET, OpenCode y Claude Code. También se inicializó `out/.git` para evitar una carrera entre los dos builds paralelos.

## 5. Decisiones de arquitectura

Primero se consultaron recomendaciones:

```bash
.venv/bin/python -m forge advise "Intervenciones"
.venv/bin/python -m forge advise "Repuestos del Taller"
```

Las decisiones se guardaron en:

```text
decisiones/intervenciones.toml
decisiones/repuestos-del-taller.toml
```

### Intervenciones

```text
C# · Clean + DDD · microservicio · MongoDB
cqrs, pipeline, memento, state, specification,
eventos, outbox, acl, cifrado, cache
```

Se asignó a Claude porque era el dominio más complejo: kernel C#, Clean + DDD, MongoDB, diez patrones y 109 símbolos.

### Repuestos del Taller

```text
Python · hexagonal · microservicio · PostgreSQL
memento, cache, cifrado, eventos, outbox, acl, state
```

Se agregó `state` para cubrir los ciclos de vida de existencias y solicitudes de reposición.

Validación:

```bash
.venv/bin/python -m forge check "Intervenciones"
.venv/bin/python -m forge check "Repuestos del Taller"
```

## 6. Manifiestos y órdenes

```bash
.venv/bin/python -m forge -d "Intervenciones" render
.venv/bin/python -m forge -d "Repuestos del Taller" render
```

Manifiestos derivados del modelo:

```text
Intervenciones: 109 símbolos
Repuestos:      100 símbolos
```

Órdenes de trabajo:

```text
.forge/intervenciones/work/
.forge/repuestos-del-taller/work/
```

## 7. Configuración de motores

OpenCode usa `forge.toml`:

```toml
[agent]
engine = "opencode"
model = "github-copilot/auto"
opencode_agent = "forge-orchestrator"
```

Ese modelo fue probado y resolvió `gpt-5.6-luna` mediante GitHub Copilot OAuth. Claude usa `forge.claude.toml`:

```toml
[agent]
engine = "claude"
model = ""
```

La configuración separada permite usar motores distintos sin que dos procesos escriban el mismo dominio.

## 8. Build de Intervenciones

```bash
.venv/bin/python -m forge -c forge.claude.toml build "Intervenciones" --laps 6
```

Etapas:

```text
S00-ir, S01-manifest, S02-scaffold, S03-adr,
S10-kernel, S11-domain, S12-application, S13-adapters,
S30-smoke, S40-microfrontend, S50-verify, S60-report
```

Resultado: `109/109 = 100%` y todas las etapas en `passed`.

## 9. Build de Repuestos del Taller

Primer comando, con OpenCode:

```bash
.venv/bin/python -m forge build "Repuestos del Taller" --laps 6
```

Los modelos gratuitos alcanzaron su límite. Se cambió OpenCode a GitHub Copilot y se conservó el estado.

Para continuar con Claude, primero se detiene cualquier proceso de OpenCode que use Repuestos y luego se ejecuta:

```bash
.venv/bin/python -m forge -c forge.claude.toml build "Repuestos del Taller" --laps 6
```

El estado está en `.forge/repuestos-del-taller/state.json`; las etapas `passed` no se repiten.

## 10. Problema de Docker

S30-smoke inicialmente falló por permisos sobre `/var/run/docker.sock`, no por el código. El socket era `root:docker` y el usuario no pertenecía al grupo `docker`.

Solución:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
docker ps
```

Si se usa `newgrp`, no hace falta cerrar sesión; de lo contrario, se debe iniciar una sesión nueva.

## 11. Ensamblado final

Cuando ambos dominios tengan todas las etapas aprobadas:

```bash
.venv/bin/python -m forge assemble
```

Esto integra los dominios reales, el contrato final del bus, el bus de eventos, los simuladores, el gateway, los microfrontends y Docker Compose.

No se ejecuta mientras otro build todavía esté escribiendo archivos.

## 12. Ejecutar Intervenciones

```bash
cd /home/dishyma/repos/archiforge/out/.platform/intervenciones
docker compose up --build --wait
```

Gateway: `http://localhost:8080`.

Endpoints útiles: `/sim/health`, `/sim/received`, `/sim/simulate/<contexto>/<evento>` y `/api/intervenciones/...`.

Smoke completo:

```bash
cd /home/dishyma/repos/archiforge/out
python3 services/intervenciones/smoke/smoke.py
```

Apagar:

```bash
cd /home/dishyma/repos/archiforge/out/.platform/intervenciones
docker compose down -v
```

## 13. Ejecutar los microfrontends

```bash
cd /home/dishyma/repos/archiforge/out/frontend/mfe-intervenciones
npm run dev
```

Para Repuestos se usa `out/frontend/mfe-repuestos-del-taller/` de la misma manera. Cada frontend se genera como Web Component, por ejemplo `<mfe-intervenciones></mfe-intervenciones>`.

## 14. Real versus simulado

Dominios reales:

```text
Intervenciones
Repuestos del Taller
```

Cada uno tiene servicio, dominio, aplicación, adaptadores, persistencia, API, pruebas, despliegue, smoke test y microfrontend.

Los demás contextos se emulan mediante servicios que publican y reciben eventos. Los simuladores se generan desde el mismo IR y contrato del bus; no se inventan contratos separados.

## 15. Lista final de aceptación

- [ ] Ambos dominios tienen todas las etapas en `passed`.
- [ ] Ambos tienen al menos 90% de conformidad.
- [ ] Los ADR justifican arquitectura, BD, patrones y despliegue.
- [ ] Se usan C# y Python, Clean + DDD y Hexagonal, MongoDB y PostgreSQL.
- [ ] Cada aplicación cubre caché, memento/estado, cifrado y despliegue.
- [ ] Ambos smoke tests pasan.
- [ ] Ambos microfrontends compilan.
- [ ] `forge assemble` termina correctamente.
- [ ] El contrato final del bus y los simuladores están generados.
- [ ] Se conservan `verificacion.md` y `trazabilidad.md`.

## 16. Archivos importantes

```text
forge.toml
forge.claude.toml
decisiones/intervenciones.toml
decisiones/repuestos-del-taller.toml
inputs/DronesArchimate/modelo/drones-mantenimiento.archimate
reference/evaluacion_final.md
.forge/intervenciones/
.forge/repuestos-del-taller/
out/services/intervenciones/
out/services/repuestos-del-taller/
out/frontend/mfe-intervenciones/
out/frontend/mfe-repuestos-del-taller/
out/docs/intervenciones/
out/docs/repuestos-del-taller/
```

## Resumen

El ArchiMate ya era un insumo del proyecto. ArchiForge lo leyó en `S00-ir`, derivó el IR y generó manifiestos, órdenes, código, pruebas, plataformas y microfrontends a partir del modelo y de las decisiones arquitectónicas tomadas para cada dominio.
