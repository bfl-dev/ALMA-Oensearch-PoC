# Plan de entrega y preparación de tareas

**Estado:** propuesta documental. No se han creado milestones/issues de implementación ni asignado ejecución a agentes.

## Hitos propuestos

| Hito | Resultado | Condición de salida | Objetivo |
| --- | --- | --- | --- |
| M0 — Definición revisada | Alcance, requisitos, referencias, C4/ADR y contratos mínimos coherentes | Aprobación explícita del propietario y registro del alcance autorizado | Iniciar el 1 de noviembre de 2026 |
| M1 — Demo esencial | Dos fuentes, recuperación/replay, análisis explicable y evidencia en GitHub | Criterios esenciales ejecutados; pendientes y limitaciones visibles | Antes del 3 de noviembre: objetivo 2 de noviembre, America/Santiago |
| M2 — Extensiones | Mejoras priorizadas desde la evidencia de M1 | Alcance nuevo aprobado | Sin fecha comprometida |

M1 depende de cerrar M0 y autorizar implementación. No asignar una fecha ficticia de finalización ni omitir verificación para cumplir el plazo. Si M1 no cabe, renegociar el alcance con el propietario o publicar honestamente un avance.

## Backlog candidato

Convertir estas filas en issues al cerrar la definición. Los IDs son locales, no números de GitHub.

| Tarea | Resultado revisable | Dependencias | Tipo |
| --- | --- | --- | --- |
| DOC-01 | Revisar alcance esencial y completar registro de aprobación | PR documental | Revisión con propietario |
| DOC-02 | Obtener `alma-internship.md` y cotejar referencia histórica | Ninguna | Investigación documental |
| DOC-03 | Evaluar ACS real y documentar viabilidad/fallback | DOC-01 | Investigación, sin desarrollo previo a autorización |
| DOC-04 | Cerrar C4, ADR-0002, herramienta y topología | DOC-01, DOC-02, DOC-03 | Diseño |
| DOC-05 | Cerrar contratos y parámetros de aceptación | DOC-04 | Diseño |
| IMP-01 | Entorno local reproducible, versiones y persistencia | DOC-05 + autorización explícita | Implementación futura |
| IMP-02 | Fuentes ONLINE/OFFLINE y manifiestos de corpus | IMP-01 | Implementación futura |
| IMP-03 | Adaptación, identidad, checkpoints y transporte | IMP-02 | Implementación futura |
| IMP-04 | Indexación, errores parciales, reintentos y cuarentena | IMP-03 | Implementación futura |
| VAL-01 | Evidencia de recuperación, replay y repeticiones | IMP-04 | Pruebas futuras |
| IMP-05 | Consultas, dashboard e incidente reproducible | IMP-04 | Implementación futura |
| IMP-06 | Correlación explicable y patrones básicos | IMP-05 | Implementación futura |
| DOC-06 | Informe documental de migración | DOC-02, versiones de DOC-04 | Investigación |
| DEM-01 | Guion, evidencia, reproducción y estado de release | VAL-01, IMP-06, DOC-06 | Entrega futura |

El orden no exige un servicio ni un PR por fila. Mantener tareas pequeñas y consolidar cuando reduzca coordinación sin perder revisión.

## Estructura de un issue para agente

Usar la [plantilla de tarea](../../.github/ISSUE_TEMPLATE/task.md). Debe incluir objetivo observable, alcance autorizado, exclusiones, requisitos/ADR/contratos aplicables, dependencias, archivos permitidos, criterios de aceptación y evidencia exigida. Una tarea sin contrato estable vuelve a diseño; no debe inventar la interfaz.

Antes de delegar: indicar revisión aprobada, tarea/branch, límites y pruebas pertinentes. La entrega debe describir resultado, evidencia, riesgos y pendientes. Solo se marcará terminado lo verificado. La preparación del backlog no constituye autorización para ejecutar agentes.

## Etiquetas candidatas

Mantener pocas: `documentation`, `design`, `implementation`, `validation`, `demo`, `extension`, `blocked`. Las dependencias y criterios deben estar en el cuerpo de los issues; un milestone agrupa resultados, no sustituye aceptación.
