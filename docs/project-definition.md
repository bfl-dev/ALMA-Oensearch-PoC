# Definición formal del proyecto

**Estado:** propuesto para revisión. **Responsable de aprobación:** propietario del proyecto. **Implementación:** pendiente de autorización.

## Propósito

Construir un proyecto personal demostrable que fortalezca una postulación a la práctica ALMA 2027 mediante evidencia de diseño, recuperación de fallos e investigación de incidentes basada en logs. La primera entrega debe ser comprensible desde GitHub y reproducible en un entorno local acotado.

La observabilidad se acota inicialmente a logs y al estado operativo del pipeline. Una plataforma completa de métricas y trazas queda fuera de la demo propuesta.

## Decisiones recibidas

| ID | Decisión del propietario |
| --- | --- |
| D-01 | OpenSearch será el motor principal; la migración desde Elasticsearch se investigará documentalmente |
| D-02 | Inspiración en arquitectura histórica publicada por ALMA, sin inferir infraestructura actual |
| D-03 | Dos fuentes: ACS ONLINE real o mock con XML, y OFFLINE mediante simulador de aplicaciones web/API |
| D-04 | RabbitMQ como intermediario de mensajería persistente |
| D-05 | Ingesta continua y reprocesamiento histórico |
| D-06 | Recuperación tras fallos abruptos e interrupciones temporales de OpenSearch |
| D-07 | Evitar duplicados del pipeline preservando eventos legítimamente repetidos de ACS |
| D-08 | Búsqueda, visualización, reconstrucción de incidentes, correlación automática explicable y descubrimiento de patrones |

El orden de trabajo solicitado es: repositorio → alcance/requisitos → C4/ADR → contratos → hitos/issues/tareas → implementación y pruebas autorizadas.

## Demo esencial propuesta

No se eliminan capacidades de D-08: se reduce la complejidad de su primera versión.

| Área | Primera versión propuesta | Evidencia esperada |
| --- | --- | --- |
| ONLINE | Evaluar primero un componente ACS real; recurrir a mock XML documentado si sus dependencias impiden la demo | Procedencia, versión y limitaciones del productor; nunca afirmar integración real si se usa mock |
| OFFLINE | Simulador pequeño de una aplicación/API, con operación normal, error y recuperación | Eventos reproducibles con identificadores de solicitud/operación |
| Transporte | Una instancia local persistente de RabbitMQ y consumidores acotados | Recuperación de mensajes pendientes después de reinicio |
| Indexación | OpenSearch y visualización mediante Dashboards, topología local por evaluar | Búsquedas reproducibles y estado de ingesta visible |
| Replay | Releer un archivo histórico inmutable y solaparlo con ingesta continua | Mismo conjunto de identidades tras una o varias relecturas |
| Incidentes | Un incidente sintético conocido con contexto anterior y posterior | Línea temporal, eventos de soporte y límites de la explicación |
| Correlación | Una o dos reglas deterministas usando identificadores y ventanas temporales | Regla/version, eventos relacionados y razón del vínculo |
| Patrones | Agrupación de mensajes normalizados, frecuencia y ejemplos inspeccionables | Al menos un patrón recurrente y un mensaje fuera del grupo |
| Migración | Informe breve de compatibilidad y riesgos con fuentes | Separación entre hechos documentados, hipótesis y pruebas futuras |

Los nombres ONLINE/OFFLINE identifican las familias de origen, no modos conectado/desconectado. No se inventará un identificador compartido entre fuentes para aparentar correlación real: cualquier vínculo sintético debe declararse como parte del escenario.

## Extensiones propuestas

- Clústeres distribuidos, alta disponibilidad y pruebas de pérdida de nodos.
- Más formatos, fuentes y escenarios operacionales; integración ACS más amplia tras un mock inicial.
- Detección de anomalías, embeddings, aprendizaje automático y process mining.
- Interfaz propia, alertas externas, SSO/RBAC avanzado, métricas/trazas distribuidas y despliegue remoto.
- Migración ejecutada desde Elasticsearch: fuera del alcance solicitado; requeriría un cambio explícito.

Estas extensiones no son condición para declarar terminada la demo esencial.

## Límites de las garantías propuestas

El objetivo es recuperar eventos disponibles en una fuente persistente o aceptados por el transporte durable, dentro del volumen y ventana de interrupción acordados. Se exige definir el punto exacto de aceptación y de avance del checkpoint antes de implementar. No se promete entrega exactamente una vez de extremo a extremo.

La demo debe cubrir la terminación abrupta del productor/adaptador, del consumidor y el reinicio del broker conservando almacenamiento, además de indisponibilidad temporal de OpenSearch. La destrucción de volúmenes, pérdida física de disco, borrado de fuentes y un backlog ilimitado quedan fuera de la garantía propuesta y deben declararse en la entrega.

## Entrega antes del 3 de noviembre

Se interpreta como fecha objetivo el **2 de noviembre de 2026, America/Santiago**. El plazo obliga a priorizar y medir; no sustituye la revisión de alcance ni autoriza implementación.

Propuesta: documentar el 1 de noviembre, cerrar decisiones y contratos al inicio del trabajo siguiente, y ejecutar/demo el 2 únicamente si se autoriza y el entorno lo permite. Si falta evidencia, publicar el estado real y el pendiente; no etiquetar la demo como completa.

## Registro de revisión

| Punto pendiente | Propuesta a revisar | Estado |
| --- | --- | --- |
| Alcance esencial | La tabla de primera versión anterior | Pendiente |
| ACS real frente a mock | Priorizar real con investigación acotada; registrar el bloqueo antes de pasar a mock | Pendiente de concretar esfuerzo y fuente XML |
| Recursos y topología | Entorno local sencillo; definir número de nodos y recursos con el equipo disponible | Pendiente |
| Correlación y patrones | Reglas explicables y agrupación/frecuencias, sin ML inicialmente | Pendiente |
| Garantías | Fallos de procesos y reinicio con datos persistidos, sin pérdida de almacenamiento | Pendiente |
| Aceptación cuantitativa | Parámetros tentativos en el plan de validación | Pendiente |
| Referencia de práctica | Obtener y leer `alma-internship.md` | Pendiente |
| Autorización de implementación | Instrucción explícita del propietario después de revisar alcance | No otorgada |

Registro de aprobación: **ninguno todavía**. Cuando exista, indicar fecha, mensaje/PR que la respalda, versión documental aprobada y cambios pendientes.
