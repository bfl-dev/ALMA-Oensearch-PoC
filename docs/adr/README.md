# Architecture Decision Records

Un ADR registra contexto, elección, alternativas, consecuencias y validación necesaria. No se consideran aprobadas propuestas por el hecho de estar escritas.

| ADR | Tema | Estado |
| --- | --- | --- |
| [0001](0001-project-constraints.md) | Restricciones tecnológicas y límites recibidos | Decisiones recibidas; no es aprobación del alcance completo |
| [0002](0002-recovery-and-event-identity.md) | Recuperación e identidad de eventos | Propuesto; requiere revisión |

Usar la [plantilla](template.md) para decisiones nuevas. Evitar un ADR por detalle menor. Antes de implementar deben resolverse al menos garantías de recuperación/identidad, herramienta de procesamiento y topología local; pueden agruparse si la justificación es breve.
