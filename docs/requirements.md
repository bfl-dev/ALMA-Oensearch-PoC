# Requisitos y criterios de aceptación

**Estado:** borrador. Derivan de las decisiones recibidas y de la demo propuesta; todavía no constituyen una baseline aprobada ni resultados verificados.

## Requisitos funcionales

| ID | Requisito | Decisión | Aceptación |
| --- | --- | --- | --- |
| RF-01 | Ingerir XML de ACS real o mock documentado, preservando contenido original y procedencia | D-03 | CA-01 |
| RF-02 | Ingerir logs OFFLINE de una aplicación/API simulada | D-03 | CA-01 |
| RF-03 | Mantener ingesta continua y replay histórico mediante RabbitMQ persistente | D-04, D-05 | CA-02, CA-04 |
| RF-04 | Normalizar sin perder la distinción entre tiempo del evento y tiempo de procesamiento | D-05, D-08 | CA-01, CA-07 |
| RF-05 | Buscar y visualizar por rango temporal, origen, severidad, componente y texto | D-08 | CA-06 |
| RF-06 | Reconstruir un incidente con contexto y referencias a eventos originales | D-08 | CA-07 |
| RF-07 | Producir correlaciones automáticas con regla, versión, evidencia y explicación | D-08 | CA-08 |
| RF-08 | Descubrir patrones de mensajes mediante agrupación, frecuencias y ejemplos | D-08 | CA-09 |
| RF-09 | Investigar documentalmente la migración Elasticsearch → OpenSearch sin ejecutarla | D-01 | CA-10 |

## Requisitos de calidad

| ID | Requisito | Decisión | Aceptación |
| --- | --- | --- | --- |
| RC-01 | Recuperar el procesamiento tras fallos abruptos dentro del modelo de fallos acordado | D-06 | CA-03, CA-04 |
| RC-02 | Conservar backlog durante indisponibilidad temporal de OpenSearch y drenarlo al volver | D-06 | CA-04 |
| RC-03 | No crear duplicados por reentrega, reintento o replay del mismo evento | D-07 | CA-02, CA-03, CA-05 |
| RC-04 | Conservar dos ocurrencias legítimas aunque su XML, mensaje y timestamp coincidan | D-07 | CA-05 |
| RC-05 | Aislar entradas inválidas y errores permanentes de indexación sin pérdida silenciosa ni bloqueo indefinido de válidos | D-06 | CA-11 |
| RC-06 | Hacer reproducible y medible la demo en un entorno local documentado | Objetivo de entrega | CA-12 |

## Escenarios de aceptación propuestos

### CA-01 — Dos fuentes y normalización

Dado un corpus con manifiesto de identidades esperadas para ONLINE y OFFLINE, cuando se procesa, cada evento válido conserva origen, identidad, tiempo original, tiempo de ingesta, severidad, componente, mensaje y referencia al contenido original. La consulta recupera las identidades esperadas de ambas fuentes. La ausencia de un campo opcional se representa explícitamente; no se inventan valores ACS.

### CA-02 — Replay con solapamiento

Dado un archivo identificado de forma estable que participa en ingesta continua, cuando se relee dos veces incluyendo registros ya publicados, el conjunto y la cantidad de eventos finales son los esperados. Cambiar la ruta del mismo archivo preservando su identidad de archivo no crea nuevas ocurrencias. La política de retención/índice de destino debe permitir esta propiedad durante la ventana soportada.

### CA-03 — Fallos en límites de confirmación

Cuando se termina abruptamente un adaptador antes y después de recibir confirmación del broker, el checkpoint no causa pérdidas al reiniciar. Cuando el consumidor cae antes de indexar o después de indexar y antes de confirmar el mensaje, el reinicio converge al mismo conjunto esperado. Incluir una respuesta de indexación perdida para simular resultado incierto. Si el destino se confirma antes de persistir durablemente el evento, el escenario falla.

### CA-04 — OpenSearch temporalmente fuera de servicio y broker reiniciado

Durante la interrupción acordada, el backlog se conserva y los procesos siguen una política acotada de espera/reintento. Tras restaurar OpenSearch, todos los eventos válidos aceptados aparecen una vez y el backlog se drena dentro del umbral acordado. En un escenario separado, reiniciar RabbitMQ con mensajes pendientes y volúmenes conservados produce el mismo resultado. La evidencia identifica qué eventos habían sido aceptados durablemente.

### CA-05 — Repetición legítima frente a duplicación técnica

Dadas dos ocurrencias ACS distintas con XML y timestamp idénticos, cuando cada una se entrega varias veces y luego se reprocesa el archivo, quedan exactamente dos eventos. Una misma ocurrencia mantiene su identidad entre ejecución continua, reinicio y replay. El oráculo utiliza coordenadas/manifiesto de origen, no el hash del cuerpo como equivalencia de ocurrencias.

### CA-06 — Búsqueda y visualización

El revisor ejecuta consultas documentadas por tiempo, origen, severidad, componente y texto, encuentra un evento conocido y observa al menos una visualización temporal y una distribución por origen/severidad. Se conservan consultas y evidencia exportable; una captura aislada no prueba conteos.

### CA-07 — Reconstrucción de incidente

Dado un incidente sintético con cronología conocida y eventos tardíos, la investigación recupera su contexto, ordena por tiempo del evento con desempate documentado y distingue observaciones de hipótesis. Las referencias permiten volver a los logs originales. No se interpreta proximidad temporal como causalidad probada.

### CA-08 — Correlación explicable

Una regla versionada vincula los eventos esperados y devuelve sus identidades, condiciones cumplidas y explicación legible. Un caso negativo con eventos cercanos pero de otra operación no se vincula. Si faltan identificadores ACS, la salida señala la inferencia y sus límites. La demostración declara cualquier relación artificial entre fuentes.

### CA-09 — Descubrimiento de patrones

Un corpus incluye mensajes de la misma familia con parámetros variables y otro mensaje distinto. El análisis devuelve grupos, plantilla o criterio de agrupación, frecuencias y ejemplos; detecta la familia repetida sin fusionar ni borrar sus eventos. Se documentan normalización y límites. No requiere entrenar un modelo.

### CA-10 — Investigación de migración

Un informe identifica versiones consideradas, APIs/clientes, mappings, consultas, visualizaciones, seguridad/plugins, transferencia de datos y riesgos relevantes. Cada conclusión distingue documentación consultada, supuesto y validación pendiente. No afirma haber migrado ni presume una versión actual de Elasticsearch en ALMA.

### CA-11 — Registros inválidos y fallos parciales

Un lote mezcla registros válidos, XML inválido y un rechazo permanente de indexación. Los válidos terminan indexados; los inválidos quedan en almacenamiento de cuarentena inspeccionable con origen, motivo e identidad/referencia para corregir y reprocesar. La confirmación solo permite retirar el mensaje original después de una disposición durable. Evaluar los resultados de cada elemento, incluyendo un lote con éxito parcial.

### CA-12 — Demo reproducible y evidencia honesta

Un revisor sigue instrucciones desde un entorno limpio con prerrequisitos declarados y obtiene los resultados acordados. El informe registra commit, versiones, hardware, configuración, corpus, conteos, tiempos y limitaciones. Todo criterio no ejecutado se marca como pendiente; no hay afirmaciones de alta disponibilidad o escala operacional sin evidencia.

Los parámetros de carga, tiempos y retención se proponen en el [plan de validación](validation.md); deben aprobarse y fijarse antes de ejecutar las pruebas.
