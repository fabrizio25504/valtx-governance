---
id: FEAT-050
titulo: Feature simple para que los empleados registren y consulten sus solicitudes de vacaciones
tags: [registro]
policies: [POL-PE-CONSENT-001]
owner: producto@valtx.pe
estado: draft
---

# Feature Specification: Feature simple para que los empleados registren y consulten sus solicitudes de vacaciones

## Contexto

Este feature permite a los empleados de la empresa registrar sus solicitudes de vacaciones de manera simple, indicando la fecha de inicio, fecha de fin, y un motivo breve. Asimismo, permite consultar el estado de dichas solicitudes (pendiente, aprobado, rechazado). La visibilidad de cada solicitud está restringida exclusivamente al empleado que la realiza y a su jefe directo. Dado que el registro involucra datos personales (identificación del empleado y motivos), se requiere aplicar la normativa de consentimiento.

## Requisitos (EARS)

- **REQ-VAC-001**: WHEN el usuario envía una nueva solicitud de vacaciones con fecha de inicio, fecha de fin y motivo THE SYSTEM SHALL registrar la solicitud con estado "pendiente" y almacenar el consentimiento previo, expreso y demostrable (timestamp + versión de política) del usuario antes de tratar sus datos personales, cumpliendo con POL-PE-CONSENT-001 (Art. 5).
- **REQ-VAC-002**: IF el usuario que intenta visualizar una solicitud de vacaciones no es el empleado solicitante ni su jefe directo THE SYSTEM SHALL bloquear el acceso al registro de la solicitud, protegiendo los datos personales asociados, cumpliendo con POL-PE-CONSENT-001 (Art. 5).
- **REQ-VAC-003**: WHEN el usuario consulta el listado de sus solicitudes de vacaciones THE SYSTEM SHALL mostrar el historial de solicitudes con su estado actual (pendiente, aprobado, rechazado) garantizando que el consentimiento para mostrar estos datos fue previamente registrado, cumpliendo con POL-PE-CONSENT-001 (Art. 13-14).

## Normas cumplidas

| Requisito | Policy Card | Artículo | Descripción |
|-----------|-------------|----------|-------------|
| REQ-VAC-001 | POL-PE-CONSENT-001 | Art. 5 | Consentimiento previo, libre, expreso, informado e inequívoco ANTES de tratar datos personales. |
| REQ-VAC-002 | POL-PE-CONSENT-001 | Art. 5 | Principio de consentimiento aplicado a la restricción de acceso a datos personales. |
| REQ-VAC-003 | POL-PE-CONSENT-001 | Art. 13-14 | Alcances y límites del tratamiento de datos personales. |
