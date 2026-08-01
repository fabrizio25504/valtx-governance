---
id: FEAT-052
titulo: Job programado que aplica retención y purga de logs de acceso
tags: [logs, perfil, purga, retencion, exportar_datos]
policies: [POL-PE-MINIM-004, POL-PE-ARCO-005]
owner: producto@valtx.pe
estado: draft
module: src/job_programado_que_aplica.py
---

# Feature Specification: Job programado que aplica retención y purga de logs

**Feature Branch**: `052-job-programado-que-aplica`

**Created**: 2023-10-25

**Status**: Draft

**Input**: User description: "Job programado que aplica la retención definida sobre los logs de acceso al directorio interno y ejecuta la purga de los registros vencidos. Antes de la purga, el titular puede exportar datos de su propio historial de accesos en formato estructurado desde su perfil."

## Contexto

El sistema mantiene un registro de los accesos de los usuarios al directorio interno. Para cumplir con la normativa de protección de datos personales, es necesario aplicar una política de retención estricta que minimice el tiempo de vida de estos datos y permita la purga automática de los registros vencidos. Previo a la purga, el titular de los datos debe tener la capacidad de exportar su propio historial de accesos en un formato estructurado, garantizando así el ejercicio de sus derechos ARCO y la portabilidad.

## Requisitos (EARS)

- **REQ-RET-001**: WHEN el job programado se ejecuta diariamente THE SYSTEM SHALL aplicar la política de retención definida sobre los logs de acceso al directorio interno y purgar los registros vencidos automáticamente, cumpliendo POL-PE-MINIM-004 (Arts. 6, 7, 20).
- **REQ-PORT-001**: WHEN el titular solicita exportar su historial de accesos desde su perfil antes de la purga THE SYSTEM SHALL generar y entregar los datos en un formato estructurado, cumpliendo POL-PE-ARCO-005 (Arts. 19, 76).

## Normas cumplidas

| Requisito | Policy Card | Artículo | Descripción |
|-----------|-------------|----------|-------------|
| REQ-RET-001 | POL-PE-MINIM-004 | Arts. 6, 7, 20 | Minimización, proporcionalidad y supresión automática al expirar retención |
| REQ-PORT-001 | POL-PE-ARCO-005 | Arts. 19, 76 | Derecho de acceso y portabilidad en formato estructurado |
