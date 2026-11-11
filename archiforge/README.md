# ArchiForge — generador usado en la entrega V3

Copia del orquestador que generó el producto de `../entrega-v3/` a partir del modelo ArchiMate.

**No hace falta ejecutarlo** para levantar la entrega: `entrega-v3/` ya contiene el código generado. Este directorio existe para poder **extender** la solución (por ejemplo, implementar un contexto que hoy está simulado) sin rehacer lo ya construido.

## Qué hay aquí

```text
archiforge/
├── forge/                orquestador (etapas, puertas, manifiesto, scaffold)
├── prompts/              órdenes de trabajo que reciben los agentes por etapa
├── catalog/              catálogo de patrones
├── decisiones/           decisiones de arquitectura de los dos dominios
├── config/               contratos de payload de eventos
├── reference/            guía DDD y material de la evaluación
├── inputs/DronesArchimate/  copia del modelo y documentos usados como entrada
├── tests/                pruebas del generador
├── forge.toml            configuración OpenCode
└── forge.claude.toml     configuración Claude Code
```

## Instalación

```bash
cd archiforge
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m forge doctor
```

## Verificar el estado actual

```bash
.venv/bin/python -m forge check "Intervenciones"
.venv/bin/python -m forge check "Repuestos del Taller"
.venv/bin/python -m pytest tests
```

## Implementar un contexto que hoy está simulado

```bash
.venv/bin/python -m forge advise "Flota y Componentes"
# decidir lenguaje, arquitectura, estilo, BD y patrones
.venv/bin/python -m forge build "Flota y Componentes"
```

Después se vuelve a ensamblar la plataforma completa:

```bash
.venv/bin/python -m forge assemble
```

El contrato del bus se regenera de forma determinista con el conjunto real actualizado, así que los servicios existentes siguen encajando.

## Estado de las etapas

El avance vive en `.forge/<dominio>/state.json` y **no se versiona** (es estado local de ejecución). Las etapas aprobadas se registran una vez y no se repiten al reanudar.

## Configuración de motores

- `forge.toml` → `engine = "opencode"`, `model = "github-copilot/auto"`
- `forge.claude.toml` → `engine = "claude"`

El motor es global por archivo de configuración; por eso hay dos archivos si se quiere construir un dominio con cada herramienta.

Guía completa del proceso: [`../docs/guia-ejecucion-v3.md`](../docs/guia-ejecucion-v3.md).
Documentación original de la herramienta: [`README-archiforge.md`](README-archiforge.md).
