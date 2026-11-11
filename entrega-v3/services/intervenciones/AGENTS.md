# Servicio «Intervenciones» (csharp · clean-ddd · microservicio · mongodb)

Generado a partir del modelo ArchiMate (evaluación final de Arquitectura de Software, versión 3) según las decisiones del arquitecto
(`docs/intervenciones/decisiones.toml`). Patrones elegidos: acl, cache, cifrado, cqrs, eventos, memento, outbox, pipeline, specification, state.

- Contratos de integración: ver el contrato del bus del ensamblado (`docs/contrato-bus.md`) y `docs/intervenciones/`.
- Nombres de dominio en español, sin tildes, como el modelo. SOLID, DDD, dependencias hacia adentro.
- Todo cambio de comportamiento lleva prueba; las pruebas son herméticas (sin red ni Docker).
- No hagas `git commit`: el orquestador versiona por etapa.
