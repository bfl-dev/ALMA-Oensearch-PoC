# Referencias y límites de la evidencia

Consulta documental: 1 de noviembre de 2026. Diferenciar instrucciones del propietario, fuentes leídas y documentos pendientes.

## S-01 — Publicación histórica de ALMA

Gil, J. P.; Miranda, N.; Garcés, M.; Avarias, J. **Current Status of Software Log Analysis at ALMA Observatory**. Software and Cyberinfrastructure for Astronomy V, 2018. DOI: [10.1117/12.2314247](https://doi.org/10.1117/12.2314247).

- Referencia solicitada: `Current_Status_of_Software_Log_Analysis_at_ALMA_Observatory1.pdf`.
- Estado: el archivo exacto no se encontró en los recursos disponibles. Se leyó el texto público de la publicación [subido por uno de sus autores](https://www.researchgate.net/publication/326236739_Current_status_of_software_log_analysis_at_ALMA_Observatory). No se comprobó identidad binaria con el PDF solicitado.
- Alcance: evidencia histórica de 2018; no acredita infraestructura ni procedimientos actuales.

Correspondencia resumida con el proyecto:

| Sección | Observación del artículo | Uso en este PoC |
| --- | --- | --- |
| 2.1 y 3.2 | ACS/XML, puente `alogging2mq`, RabbitMQ, Logstash y Elasticsearch/Kibana | Inspiración para desacoplar ingesta e investigación; OpenSearch es una elección del propietario |
| 2.3 y 3.3 | Fuentes OFFLINE web/API y uso de Filebeat para centralización | Motiva representar dos familias; aquí ambas usarán RabbitMQ por decisión propia |
| 4 y 5 | Exploración, análisis de procesos y herramientas analíticas | Motiva incidentes y análisis explicable; no exige reproducir sus implementaciones |

No se copió el artículo al repositorio. La licencia MIT del proyecto no se extiende a estas publicaciones.

## S-02 — Descripción de la práctica

- Referencia solicitada: `alma-internship.md`.
- Estado: **pendiente de obtener y leer**. No está en el repositorio inicial ni se encontró por ese nombre entre los archivos disponibles.
- No se creó un archivo homónimo con contenido inferido. Las afirmaciones de conversaciones previas no sustituyen el documento original.
- Pendiente: fuente y fecha de la convocatoria, rol/equipo, contenido exacto y relación verificable con el alcance. Hasta entonces no se atribuyen a ALMA requisitos oficiales desde esta referencia.

## S-03 — Confirmaciones RabbitMQ

[Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms), documentación oficial, consultada el 1 de noviembre de 2026.

Las confirmaciones de publicación y de consumo cubren tramos distintos. Se usa para fundamentar preguntas de recuperación en ADR-0002; no acredita una configuración ya implementada. Validar contra la versión elegida posteriormente.

## S-04 — Indexación por lotes en OpenSearch

[Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/), documentación oficial, consultada el 1 de noviembre de 2026.

Las operaciones de un bulk se procesan independientemente y sus resultados se informan por elemento. Se usa para exigir análisis de errores parciales. El enlace `latest` no fija la versión del proyecto; esa elección está pendiente.

## Investigación de migración pendiente

La siguiente etapa producirá una matriz breve de versiones, APIs/clientes, mappings, consultas, dashboards, seguridad/plugins y transferencia de datos con fuentes oficiales. No hay versiones actuales de ALMA verificadas ni resultados de migración en este repositorio.
