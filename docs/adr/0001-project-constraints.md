# ADR-0001 — Restricciones y decisiones recibidas

- Estado: decisiones recibidas del propietario el 1 de noviembre de 2026
- Origen: instrucciones de apertura de este trabajo; D-01 a D-08 en la [definición](../project-definition.md)
- Alcance: registra elecciones existentes; no aprueba el diseño completo ni inicia implementación

## Contexto y decisión

El proyecto busca evidencia presentable de observabilidad para una postulación personal. OpenSearch es el destino principal y RabbitMQ el intermediario persistente. Se contemplan fuentes ONLINE ACS/XML y OFFLINE simuladas, ingesta continua e histórica, recuperación de fallos, preservación de repeticiones legítimas y análisis explicable.

La migración Elasticsearch → OpenSearch será investigación documental. La arquitectura histórica publicada por ALMA es inspiración, sin asumir vigencia actual. Se debe revisar el alcance con el propietario antes de implementar.

## Opciones y límites

La elección entre motores y brokers no se reabre en este ADR: fue resuelta por el propietario. Permanecen abiertas las versiones, topología, herramientas de procesamiento y contratos. No hay evidencia de que este diseño replique la infraestructura actual de ALMA.

## Consecuencias y validación

La demo debe mostrar tanto la gestión fiable de eventos como su utilidad para investigar incidentes. El plazo exige una primera versión pequeña de cada capacidad y extensiones diferenciadas. La aceptación se establecerá mediante la revisión de [requisitos](../requirements.md) y [validación](../validation.md).
