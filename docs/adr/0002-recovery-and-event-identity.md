# ADR-0002 — Recuperación mediante reentrega e identidad estable de ocurrencia

- Estado: **propuesto; no aprobado**
- Fecha: 1 de noviembre de 2026
- Requisitos: RF-03, RC-01 a RC-05
- Contratos: CT-01, CT-02 y CT-03

## Contexto

Un proceso puede caer entre una escritura y su confirmación. Volver a procesar un evento no debe duplicarlo. Al mismo tiempo, ACS puede producir ocurrencias diferentes con cuerpo y timestamp idénticos. Identificar por contenido confunde estos casos.

RabbitMQ documenta confirmaciones de publicación y confirmaciones de consumo como mecanismos distintos [S-03]. OpenSearch documenta resultados independientes por operación de un bulk [S-04]. Estos hechos requieren evaluar cada límite; no prueban por sí solos una garantía de extremo a extremo.

## Alternativas

| Opción | Evaluación propuesta |
| --- | --- |
| Identidad por hash de cuerpo/timestamp | Descartar: colapsa repeticiones legítimas |
| UUID nuevo en cada intento o replay | Descartar: transforma reintentos en eventos nuevos |
| Identidad de ocurrencia persistente antes de publicar | Candidata: preservar entre lectura continua, reintentos y replay |
| Transacción distribuida de extremo a extremo | No priorizar para la demo por complejidad; no se promete exactly-once |

## Diseño candidato

1. Establecer coordenadas durables del evento de origen antes de publicarlo. Para archivos, evaluar una identidad inmutable de archivo/generación y una posición de registro estable. Un nombre de ruta mutable no basta.
2. Derivar o conservar un `event_id` desde esas coordenadas. Dos registros iguales en posiciones distintas conservan IDs diferentes. En mocks, persistir la identidad de ejecución y la secuencia de generación antes de entregarlos.
3. Avanzar el checkpoint solo tras confirmación de aceptación durable en el destino de ese tramo. La configuración de cola, mensajes, almacenamiento y publisher confirms debe especificarse junta; el flag de persistencia por sí solo no cierra la garantía.
4. Consumir con confirmación explícita después de indexación exitosa de cada evento, o después de su traslado durable a cuarentena cuando sea inválido de forma permanente. Evaluar también errores de publicación a cuarentena.
5. Mantener estables el ID y el destino de indexación durante la ventana soportada. La misma identidad enviada a otro índice puede producir otra copia: acordar política de índices/retención y replay antes de implementar.
6. Examinar cada resultado de un bulk. Separar éxitos, rechazos permanentes y fallos transitorios; un resultado incierto requiere un reintento idempotente. No tratar cualquier conflicto como éxito sin verificar su semántica.
7. Definir reintentos con espera, límites de mensajes en vuelo y backpressure. No borrar backlog para cumplir una latencia objetivo.

## Consecuencias y cuestiones abiertas

Se busca procesamiento al menos una vez con efecto idempotente en el destino soportado. La identidad no es una deduplicación semántica de logs. El contrato de origen y la retención forman parte de la garantía, no son detalles secundarios.

Pendiente: definición exacta de coordenadas, rotación/truncado de archivos, manifestación de su identidad al copiar, tecnología de checkpoints y cuarentena, índices, política de errores y versiones. Un cambio de parser no debe cambiar silenciosamente la identidad de una ocurrencia; su reprocesamiento requiere política de versión del resultado.

## Validación para aceptar o rechazar

CA-02 a CA-05 y CA-11. Incluir fallos antes/después de confirmaciones, pérdida de respuesta, bulk parcial y dos eventos iguales en contenido. Comparar conjuntos de identidades y contenido con un manifiesto de origen independiente.

Fuentes: [S-03 y S-04](../references/README.md). Se consultaron para fundamentar la evaluación; la compatibilidad deberá revisarse para las versiones que se elijan.
