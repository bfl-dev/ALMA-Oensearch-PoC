# Instrucciones para trabajar en este repositorio

## Estado y autorización

El proyecto está en definición. El propietario pidió revisar el alcance antes de implementar. Actualmente solo se autoriza documentación, investigación y planificación.

- No crear aplicación, simuladores, infraestructura ejecutable, contenedores, dependencias, CI ni pruebas de software hasta que el propietario autorice la implementación del alcance revisado.
- No delegar ejecución a agentes sin autorización del propietario. Los documentos de tareas son preparación, no una orden de ejecución.
- Registrar la aprobación de alcance en `docs/project-definition.md` cuando exista una instrucción explícita. La existencia o fusión de un PR documental no basta por sí sola para inferirla.
- Si una instrucción posterior del propietario autoriza trabajo, esa instrucción prevalece; actualizar el estado documental para reflejarla.

## Documentación y entrega

- Nombrar branches `<tipo>/<descripcion-en-kebab-case>` según el cambio: `feature/`, `docs/`, `fix/`, `refactor/`, `test/`, `chore/`, `ci/` o `build/`. Consultar `docs/development-workflow.md` para su correspondencia con títulos de PR.
- Para este cambio usar `docs/project-definition` y un título de PR `docs: <resultado>`.
- Mantener decisiones del usuario, propuestas y evidencia verificada diferenciadas.
- Vincular requisitos, ADR, contratos y evidencias mediante sus identificadores.
- No describir metas o pruebas pendientes como resultados obtenidos.
- No presentar el artículo de 2018 como prueba de la infraestructura actual de ALMA.
- No usar hash del mensaje, timestamp o indicador de redelivery como única identidad de un evento.
- No publicar datos operacionales de ALMA, credenciales o contenido de referencias no verificadas.
- Conservar `LICENSE` y contenido ajeno al cambio.
