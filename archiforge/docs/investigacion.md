# Investigación: generación automática de software desde un modelo ArchiMate

## Pregunta
¿Se puede construir la primera versión de las aplicaciones a partir del diagrama ArchiMate y las especificaciones complementarias,
con buenas prácticas (DDD, patrones, SOLID) y con garantía verificable de que coincide con el diseño?

## Hallazgo clave
Sí, **si se separa lo que el modelo determina de lo que requiere criterio**. Un agente de IA que lee el diagrama y escribe código es rápido pero
no reproducible, se desvía del diseño y no puede demostrar su conformidad. Un generador de plantillas puro es reproducible, pero no escribe comportamiento.
La solución es un **pipeline híbrido de tres capas**:

1. **Extracción determinista** — el `.archimate` (XML) se convierte en una representación intermedia (IR): 9 contextos, 13 agregados, 54 comandos,
   59 eventos, 24 políticas evento→comando, 37 contratos de servicio y el lenguaje ubicuo. El IR conserva el id de cada elemento.
2. **Manifiesto de símbolos** — del IR se derivan, por dominio y capa, los ~200 símbolos que el diseño exige (agregados, VOs, eventos, comandos, manejadores,
   validadores, traductores, consumidores, contratos V1, repositorios, decoradores de caché, rutas…). Es determinista: el mismo modelo produce el mismo manifiesto.
3. **Agentes con puertas de calidad** — un agente implementa cada capa; una puerta automática compila, prueba, verifica la regla de dependencias
   (`.csproj` en C#, análisis de imports en Python) y comprueba que **cada símbolo del manifiesto esté declarado en la capa correcta**. Si falla, el error se
   realimenta al agente (hasta 3 intentos). Un revisor independiente audita al final.

## Por qué cumple el requisito de «90 % acorde al diseño»
La conformidad se **mide**: `docs/trazabilidad.md` lista cada elemento del modelo, el símbolo de código que lo implementa y el archivo. El pipeline exige 100 % por capa y ≥ 90 % global.

## Lo que el modelo no dice (y cómo se maneja)
El modelo nombra comandos y eventos pero no define campos ni todas las invariantes. Se cubren con (a) los contratos de servicio (errores y precondiciones → reglas de negocio),
(b) contratos de eventos **supuestos** y editables (`config/event-payloads.json`), y (c) un registro de supuestos (`docs/supuestos.md`) que el equipo revisa. Esto es una
limitación real: la automatización es tan buena como la especificación complementaria.

## Microfrontends
La partición no sigue a los microservicios sino a los **roles** del modelo (Jefe, Técnico, Almacenista): un remote por rol que habla con varios servicios, empaquetado como
Web Component y compuesto en tiempo de ejecución por un shell mediante un manifiesto. Los formularios salen de los comandos de usuario (los comandos sin rol son reacciones a eventos y no llevan UI).

## Interoperabilidad simulada
Los 7 contextos no implementados se simulan con un bus de eventos por tópicos (hace el papel de RabbitMQ/Service Bus), entrega al-menos-una-vez e idempotencia por `eventId`, y APIs síncronas simuladas tras una capa anticorrupción.

## Trabajo futuro
Plantillas para Java; extraer invariantes de propiedades adicionales del modelo (atributos tipados en los objetos de datos); generar pruebas de contrato entre servicios; mutation testing como puerta.
