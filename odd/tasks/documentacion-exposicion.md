# Manual completo para la exposición (docs/manual)
Objetivo: documentar todo el programa y el producto para que una persona sin formación técnica lo entienda, lo use y pueda defender cada decisión.
Rama: main (commit/push solo si se pide) · Runner: revisión de enlaces y de cifras contra el repositorio

## Specs
- S1. "me gustaria que lo dejaras documentado, o sea todo, literalmente todo, con respecto, a como funciona el programa, como se organiza el archimate para que se lee y se pueda ejecutar el programa, todo hecho para que la gente del comun lo pueda entender, y pueda ver como funciona y utilizarlo"
- S2. "tambien se debe tener una documentacion donde se justifique porque se eligio estas tecnologias, porque no otras, porque los patrones que se estan usando y no otros, y asi!"
- S3. "un con graficos, pueden ser en asci que me permita ver la topologia, la forma en como se comunican las cosas, porque se uso rabbitMQ y asi"
- S4. Formato elegido por la persona: "Markdown en el repo" (carpeta `docs/manual/`, enlazado, diagramas ASCII).
- A1 (supuesto): redacción en español neutro y claro; primero la explicación sencilla y después el detalle técnico.
- A2 (supuesto): cada cifra o afirmación técnica se verifica contra el repositorio (código, modelo, pruebas) antes de escribirla; lo que es decisión del equipo se distingue de lo que decide la herramienta.
- A3 (supuesto): donde las justificaciones del equipo aún son borradores (decisiones de Repuestos), el manual lo dice y presenta el análisis técnico como propuesta de redacción.

## Tasks
- [x] T1 (S1) 00 índice · 01 qué es · 02 el modelo ArchiMate — inline
- [x] T2 (S1) 03 cómo funciona el programa · 04 guía de uso — inline
- [x] T3 (S3) 05 el producto generado (topologías y comunicación) — inline
- [x] T4 (S2) 06 justificación de tecnologías · 07 justificación de patrones — inline
- [x] T5 (S1,S2) 08 calidad y pruebas · 09 preguntas frecuentes · 10 glosario — inline
- [x] T6 verificación de enlaces, cifras y diagramas — inline

## Log
- L1 (2026-11-11) pedido original citado en S1-S3; respuesta a la pregunta de formato: "Markdown en el repo (Recomendado)".
- Ruta: todo inline (documentos relacionados que comparten cifras y términos; sin unidades independientes).
- T1-T6 hechas: 11 documentos en docs/manual (README + 01-10), 1.800 líneas aprox. Enlaces internos verificados (ninguno roto) y cifras tomadas de ejecutar el programa sobre el repositorio (812 elementos, 1.350 relaciones, 9 contextos, 13 agregados, 54 comandos, 59 eventos, 24 políticas, 33 relaciones entre contextos, 37 contratos; 110 y 100 símbolos esperados; ≈524 pruebas).
- Correcciones hechas durante la redacción por verificación contra el código: conteo de formularios (7 y 5), compuertas de estilo y SOLID descritas según su código, verificación de patrones (los 10 elegidos no tienen comprobación estructural propia; 34 de 50 sí), stock de BOM-12 en la demostración (3 tras el seed).
- Pendiente (A3): las justificaciones de Repuestos siguen como borradores «Ejemplo:»; el doc 06 lo declara y ofrece argumentos base.
