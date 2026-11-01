# Estándar de branches y pull requests

## Branches

Decisión del propietario: el prefijo refleja el tipo de cambio. Formato: `<tipo>/<descripcion-en-kebab-case>`, en minúsculas y con una descripción breve y específica. Se recomienda describir el tema en inglés para mantener consistencia en los nombres técnicos.

| Prefijo | Uso | Ejemplo | Tipo en título de PR |
| --- | --- | --- | --- |
| `feature/` | Capacidad nueva | `feature/historical-replay` | `feat:` |
| `docs/` | Documentación y definición | `docs/project-definition` | `docs:` |
| `fix/` | Corrección de comportamiento | `fix/replay-event-identity` | `fix:` |
| `refactor/` | Reorganización sin cambiar comportamiento | `refactor/event-normalization` | `refactor:` |
| `test/` | Pruebas y fixtures | `test/consumer-recovery` | `test:` |
| `chore/` | Mantenimiento y herramientas auxiliares | `chore/update-tooling` | `chore:` |
| `ci/` | Automatización de integración/entrega | `ci/documentation-checks` | `ci:` |
| `build/` | Sistema de build, empaquetado o dependencias | `build/pin-runtime-dependencies` | `build:` |

La correspondencia de títulos es una convención propuesta para acompañar el estándar de branches; el propietario ha solicitado explícitamente el prefijo por tipo. Si hay cambios relacionados de varios tipos, elegir el propósito principal del PR. Si no están relacionados, separarlos. No crear validadores ni CI para imponer esta convención durante la etapa de definición.

## Pull requests

Trabajar desde `main` en una branch del tipo correspondiente, abrir un PR con resultado y validación, y enlazar requisitos/ADR/contratos cuando apliquen. La [plantilla](../.github/pull_request_template.md) recoge esa información.

Este PR documental usa `docs/project-definition`. Su revisión de documentos no autoriza implementar: la aprobación del alcance y su autorización deben quedar registradas explícitamente según [AGENTS.md](../AGENTS.md).
