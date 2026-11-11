# Convenciones del proyecto

## Nombres
- Servicios: sustantivo + verbal («Programación de mantenimiento preventivo»); nombre = resultado de negocio, no tecnología.
- Procesos: verbo en infinitivo + objeto («Programar intervención»).
- Eventos: participio pasado («Intervención ejecutada»); comandos: imperativo en el modelo de aplicación («Cerrar orden de trabajo»); eventos de dominio: pasado («Orden de trabajo cerrada»).
- Objetos de negocio y de datos: sustantivo singular («Orden de trabajo»).
- Vistas: `V05 - Dominios`, `V06a - Agregados Flota y Componentes`, etc.
- Un mismo concepto = un solo elemento en el árbol del modelo, arrastrado a varias vistas (nunca copias).

## Colores de la notación
| Capa | Relleno |
|---|---|
| Motivación | #ADB0FF |
| Estrategia | #F5DEAA |
| Negocio | #FEFF99 |
| Aplicación | #F0FFFF |
| Grupos / dominios | Core #7ED3DC · Soporte #C3EEF2 · Genérico #E9F9FB |
| Externos | gris #DCDCDC (propiedad `Externo = Sí`) |
| Impacto en V2 | Directo #EE8A2B · Parcial #F4A640 · Indirecto #F7C97A · Sin impacto #F5DEAA |

## Relaciones
Asociación (línea continua) · Influencia (discontinua, punta abierta; `+` refuerza, `−` limita; solo entre elementos de motivación) · Realización (punteada, triángulo hueco) · Serving (línea con punta abierta, del proveedor al consumidor) · Access (punteada, solo comportamiento → pasivo) · Assignment (punto + flecha) · Composición/Agregación (rombo relleno/hueco) · Triggering (línea con flecha rellena) · Flow (discontinua con flecha rellena).

## Propiedades de los elementos
`Fuente` (pregunta P-xx y hallazgo H-xx de Fase00), `Fase`, y las propias de cada tipo (`Impacto`, `Clasificación`, `Rol`, `Meta`, `Fecha`, `Alcance`, `Externo`, `ID`, `Versión`...).

## Trabajo con el `.archimate` y los documentos
- El modelo vive en `modelo/drones-mantenimiento.archimate` (más los parciales por fase en `modelo/por_fase/`) y las imágenes en `vistas/`; se edita por turnos para no generar conflictos.
- Los `.md` de `FaseNN/`, `docs/` y el `README.md` son el documento del equipo.
- Commits: `faseX: descripción (Nombre)`; un commit = una idea. Para el modelo rige además el protocolo de turnos (`git pull` antes de empezar, `git push` al terminar) porque dos regeneraciones simultáneas entran en conflicto.
