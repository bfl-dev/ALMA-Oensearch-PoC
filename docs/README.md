# Índice de documentación

Estado al 1 de noviembre de 2026: **borrador para revisión de alcance**. La implementación no está autorizada.

## Ruta de lectura

1. [Definición del proyecto](project-definition.md): propósito, decisiones recibidas, demo esencial, extensiones y revisión pendiente.
2. [Requisitos](requirements.md): comportamiento esperado y criterios de aceptación propuestos.
3. [Arquitectura](architecture/README.md): vistas C4 conceptuales y preguntas que requieren evaluación.
4. [ADR](adr/README.md): decisiones recibidas y propuestas con sus consecuencias.
5. [Contratos](contracts/README.md): límites, identidad, errores y garantías por especificar.
6. [Validación](validation.md): escenarios, oráculo de conteo y evidencia de demostración.
7. [Planificación](planning/README.md): hitos, dependencias y preparación de issues/tareas para agentes.
8. [Referencias](references/README.md): fuentes leídas, alcance de la evidencia y referencias pendientes.
9. [Flujo de trabajo](development-workflow.md): estándar de branches, títulos de PR y revisión.

## Convenciones

| Estado | Significado |
| --- | --- |
| Decisión recibida | Elección explícita del propietario; no implica implementación |
| Propuesto | Recomendación pendiente de revisión |
| Aprobado | Aceptado explícitamente por el propietario, con registro de fecha y alcance |
| Verificado | Respaldado por lectura de fuente o evidencia reproducible identificada |
| Pendiente | No definido, no obtenido o no ejecutado |

Identificadores: `D-xx` decisiones recibidas, `RF-xx` requisitos funcionales, `RC-xx` requisitos de calidad, `CA-xx` escenarios de aceptación, `CT-xx` contratos y `ADR-xxxx` decisiones de arquitectura. Un criterio escrito no es una prueba ejecutada.

## Cierre de la definición

Antes de implementar deben acordarse el alcance esencial, las garantías de recuperación, los contratos mínimos y los criterios de demo. El [registro de revisión](project-definition.md#registro-de-revisión) identifica lo pendiente. Las plantillas de [issue](../.github/ISSUE_TEMPLATE/task.md) y [PR](../.github/pull_request_template.md) facilitan la trazabilidad posterior.
