# Contratos entre componentes

**Estado:** inventario propuesto, no contrato de software aprobado. No hay schemas, APIs ni configuración ejecutable en esta etapa.

## Límites a especificar

| ID | Límite | Contenido mínimo del contrato | Aceptación |
| --- | --- | --- | --- |
| CT-01 | Fuente/archivo → adaptador | Formato y framing XML/JSON, encoding, reloj, procedencia, identidad estable de ocurrencia, rotación y replay | CA-01, CA-02, CA-05 |
| CT-02 | Adaptador → RabbitMQ | Envelope versionado, routing, persistencia, confirmación durable, checkpoint, backpressure y mensaje no enrutable | CA-03, CA-04 |
| CT-03 | RabbitMQ → procesador → OpenSearch/cuarentena | Validación, mappings, ID/índice, bulk parcial, reintentos, confirmación y disposición durable de errores permanentes | CA-03, CA-04, CA-11 |
| CT-04 | Eventos almacenados → análisis/visualización | Consulta temporal, referencias originales, explicación de correlación y salida de patrones | CA-06 a CA-09 |

Los contratos describen fronteras lógicas; no obligan a crear cuatro servicios.

## Modelo mínimo candidato

| Concepto | Semántica a acordar |
| --- | --- |
| `schema_version` | Versión del envelope; política de compatibilidad y rechazo de versiones desconocidas |
| `event_id` | Identidad de una ocurrencia original, estable en reentrega/reinicio/replay |
| `source` | Familia ONLINE/OFFLINE, productor, entorno y coordenadas durables de origen |
| `event_time` | Tiempo declarado por el origen, formato/zona y tratamiento de ausencia o error |
| `ingested_at` | Tiempo de ingesta, distinto del tiempo original; no participa en identidad |
| `severity`, `component`, `message` | Campos normalizados con procedencia y preservación de valores no mapeados |
| `raw` o referencia durable | Recuperación del registro original sin reconstruirlo desde una plantilla |
| `correlation_keys` | IDs observados en origen o inferidos explícitamente, con su procedencia |
| Metadatos de procesamiento | Versión del parser, replay/intent y diagnóstico; separados de la identidad original |

Los nombres de campos son candidatos. Longitudes, tipos, obligatorios/opcionales, timestamps inválidos, XML multilinea, caracteres y límites de tamaño deberán fijarse con ejemplos reales o fixtures documentados antes de implementar.

## Invariantes de identidad

- Mismo evento de origen, misma identidad, aunque cambie el número de intentos o el modo de ingesta.
- Ocurrencias distintas, identidades distintas, aunque todos sus campos de negocio coincidan.
- El tiempo de ingesta, delivery tag, bandera de redelivery o UUID por intento no determinan identidad de origen.
- Un hash del contenido puede comprobar integridad, pero no distingue ocurrencias idénticas.
- El replay conserva identidad de archivo/generación y posición; no infiere automáticamente que dos archivos iguales representan los mismos eventos.
- La identidad se conserva también en cuarentena y su reproceso. El índice de destino y la ventana de retención forman parte del contrato de idempotencia.

## Resultado mínimo del análisis

Una correlación debe incluir identificadores de eventos, regla y versión, condiciones cumplidas, ventana y explicación, indicando si el vínculo es observado o inferido. Un patrón debe incluir su criterio/plantilla, frecuencia y ejemplos originales. Ninguna salida modifica ni elimina los eventos de origen.

## Entregables de la siguiente etapa

1. Tabla de campos aprobada, ejemplos ONLINE/OFFLINE válidos e inválidos y política de evolución.
2. Schema del envelope y catálogo de errores/disposiciones, después de aprobar alcance.
3. Reglas exactas de identidad/checkpoint, confirmaciones y destino, consistentes con ADR-0002.
4. Ejemplos verificables de correlación y patrón que implementen CA-08/CA-09.
