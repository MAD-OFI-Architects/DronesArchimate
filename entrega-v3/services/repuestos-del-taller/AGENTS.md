# Servicio «Repuestos del Taller» (python · hexagonal · microservicio · postgresql)

Generado a partir del modelo ArchiMate (evaluación final de Arquitectura de Software, versión 3) según las decisiones del arquitecto
(`docs/repuestos-del-taller/decisiones.toml`). Patrones elegidos: acl, cache, cifrado, eventos, memento, outbox, state.

- Contratos de integración: ver el contrato del bus del ensamblado (`docs/contrato-bus.md`) y `docs/repuestos-del-taller/`.
- Nombres de dominio en español, sin tildes, como el modelo. SOLID, DDD, dependencias hacia adentro.
- Todo cambio de comportamiento lleva prueba; las pruebas son herméticas (sin red ni Docker).
- No hagas `git commit`: el orquestador versiona por etapa.
