# Validación y demostración

**Estado:** plan propuesto. No se han ejecutado pruebas de software ni medido estas capacidades.

## Parámetros tentativos para revisar

Los valores siguientes son objetivos de aceptación locales propuestos, no rendimiento observado ni requisitos atribuidos a ALMA. Ajustarlos con recursos y versiones conocidos, antes de ejecutar.

| Parámetro | Propuesta inicial |
| --- | --- |
| Corpus determinista | 1.000 ocurrencias ONLINE y 1.000 OFFLINE, con manifiesto independiente |
| Repetición legítima | Incluir al menos un par ACS de XML y timestamp idénticos con coordenadas distintas |
| Históricos | Reprocesar el corpus dos veces e incluir solapamiento con lectura continua |
| Flujo continuo | 10 eventos/s agregados durante 2 minutos, en un escenario separado del conteo de corpus |
| Interrupción de OpenSearch | 60 segundos dentro de la ejecución continua |
| Recuperación | Backlog drenado en 120 segundos tras restauración, con recursos declarados |
| Pérdida/duplicación | Cero eventos válidos aceptados perdidos; cero copias adicionales por identidad tras converger |
| Búsqueda | Consultas reproducibles correctas; registrar tiempos sin prometer un SLO aún |
| Retención y replay | Definir explícitamente ventana soportada; no probar solo en índices recién creados |

Un escenario que falle sigue fallando aunque el total global coincida por compensación entre pérdidas y duplicados.

## Oráculo y evidencia

El manifiesto del corpus define las ocurrencias originales y sus coordenadas antes del pipeline. Comparar conjuntos de identidades, multiplicidad y contenido contra ese manifiesto; no generar el oráculo únicamente con la misma función de identificación que se está validando.

Registrar separadamente: producidos, disponibles en origen persistente, aceptados durablemente por el broker, indexados, pendientes, puestos en cuarentena y reintentados. Los descartes no pueden ocultarse dentro de un contador de procesados.

Esperar la condición documentada de visibilidad de búsqueda y el final de los reintentos antes de contar. Un evento reconocido como ya procesado necesita validación de identidad/contenido/destino conforme al contrato. Los inválidos se contabilizan en cuarentena, no como eventos válidos indexados.

## Matriz mínima

| Escenario | Criterios | Evidencia futura |
| --- | --- | --- |
| Dos fuentes y corpus controlado | CA-01, CA-06 | Manifiesto, consultas y exportación de resultados |
| Replay y solapamiento | CA-02, CA-05 | Conjuntos antes/después, coordenadas y casos de repetición |
| Caída de adaptador en confirmación | CA-03 | Checkpoints antes/después y reconciliación de identidades |
| Caída de consumidor y respuesta perdida | CA-03 | Punto de fallo, reentrega y estado final |
| Interrupción OpenSearch | CA-04 | Backlog/tiempo y reconciliación al recuperar |
| Reinicio de RabbitMQ con pendientes | CA-04 | Estado durable y resultados después del reinicio |
| Bulk parcialmente fallido y registro inválido | CA-11 | Resultado por evento y cuarentena recuperable |
| Incidente con eventos tardíos | CA-07, CA-08 | Línea temporal, regla explicada y caso negativo |
| Patrones de mensajes | CA-09 | Grupos, frecuencias, ejemplos y límites |
| Investigación y reproducción | CA-10, CA-12 | Informe con fuentes e instrucciones verificadas |

Cada ejecución debe identificar commit, versiones, hardware, configuración y datos, comando/procedimiento utilizado, resultado esperado/obtenido y enlaces a evidencia. Los scripts y pruebas se escribirán cuando se autorice implementar.

## Guion de presentación propuesto

1. Explicar problema, inspiración histórica y alcance independiente del proyecto.
2. Mostrar ambas fuentes, una consulta conocida y visualizaciones.
3. Reconstruir el incidente y justificar la correlación con sus eventos de soporte.
4. Mostrar patrón recurrente con ejemplos; distinguir agrupación analítica de identidad de ocurrencia.
5. Interrumpir OpenSearch, observar backlog, restaurar y verificar recuperación.
6. Reprocesar históricos y mostrar que se conservan repeticiones legítimas sin duplicados técnicos.
7. Exponer evidencia de fallos abruptos, investigación de migración y limitaciones pendientes.

El video puede resumir pruebas más largas, pero debe enlazar su evidencia reproducible. Un README con metas no constituye una demo ejecutada.
