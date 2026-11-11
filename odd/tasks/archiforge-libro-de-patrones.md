# Libro de patrones completo (fase 2)
Objetivo: que el catálogo contenga todos los patrones relevantes y que elegir uno tenga consecuencias verificables en lo generado.
Rama: main · Runner: `archiforge/.venv/bin/python -m pytest archiforge/tests`

## Specs
- S1. "porque solo hay esos patrones deberian ser todos los que existen, todos, no solo esos": GoF (23) + dominio/aplicación/persistencia + integración y resiliencia; ≥ 50 entradas.
- S2. "usa tambien refactoring guru": cada ficha enlaza su referencia (refactoring.guru para GoF; Fowler y microservices.io/Azure para el resto); texto propio, sin copiar.
- S3. "no se sugiera nada, solo que uno sea el que elija": fichas informativas; el arquitecto elige cuáles y DÓNDE se aplican (`aplicar_en`).
- S4. "que la forma en que los haga, sea determinada": el agente recibe estructura canónica, principios y dónde aplicarlo; el verificador comprueba estructura (detectores en C#, Python y Java) y que el ADR cite tantas clases reales como roles.

## Tasks
- [x] T1 (S1,S2) Catálogo en 6 archivos TOML (50 patrones, 35 enlaces verificados con HTTP 200)
- [x] T2 (S3) `aplicar_en` obligatorio para patrones sobre código arbitrario; dependencias (`requiere`)
- [x] T3 (S4) `forge/patrones.py` (8 chequeos) + `patterns_gate` + ADR por roles
- [x] T4 (S3,S4) Prompts con estructura/dónde/ADR; TUI con «dónde se aplica» y referencia por categoría; `forge patterns --categoria`
- [ ] T5 (S4) Fase 3 pendiente: guías por decisión (estilo/arquitectura/SOLID) inyectadas en los prompts

## Log
- L1 (2026-11-11) "Dale" (iniciar fase 2 tras la propuesta del libro de patrones).
- L0 petición original: "porque solo hay esos patrones deberian ser todos los que existen, todos, no solo esos, hay muchas cosas que faltan pulir".
- Risk T3: item 3 leve (el gate de ADR ahora exige más clases solo para patrones nuevos con `min_clases`; los 10 anteriores no cambian) y T2 (nueva validación solo para patrones nuevos). Sin verificador independiente (el usuario rechazó subagentes).
- Verificado: 158 pruebas; detectores con positivos/negativos en 3 lenguajes; órdenes de trabajo reales renderizadas; capturas de la TUI.
- Límite honesto: los chequeos son heurísticos (la forma existe; no se juzga si el patrón está bien aplicado). Facade, Adapter, Mediator, Flyweight, Iterator, Service Layer, Domain Services y similares dependen del ADR + cableado, sin detector propio.
