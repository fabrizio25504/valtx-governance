---
id: FEAT-051
titulo: Calendario interno de eventos
tags: [formulario, purga, retencion, registro]
policies: [POL-PE-MINIM-004, POL-PE-CONSENT-001]
owner: producto@valtx.pe
estado: draft
---

# Feature Specification: Calendario interno de eventos

**Feature Branch**: `051-calendario-interno-de-eventos`

**Created**: 2023-10-25

**Status**: Draft

**Input**: User description: "Calendario interno de eventos de la empresa (capacitaciones, charlas, reuniones generales). Un organizador crea el evento con titulo, descripcion, fecha, hora y lugar. Los empleados ven el calendario y se inscriben a los eventos abiertos mediante un formulario de inscripcion que pide nombre, area y correo corporativo. El registro de cada inscripcion guarda quien se inscribio y cuando; el empleado puede cancelar su inscripcion en cualquier momento. El organizador ve la lista de inscritos de sus propios eventos para controlar el aforo. Se define un plazo de retencion: la purga de los datos de inscripcion ocurre 90 dias despues de terminado el evento."

## Contexto

El feature permite la gestion de eventos internos de la empresa. Los organizadores pueden crear eventos y visualizar los inscritos para control de aforo. Los empleados pueden visualizar el calendario e inscribirse mediante un formulario que captura datos personales. Debido a la captura de datos personales, se aplican las normativas de minimización y consentimiento. Los datos de inscripcion seran purgados automaticamente 90 dias despues de la finalizacion del evento.

## Requisitos (EARS)

- **REQ-EVT-001**: WHEN el organizador crea un evento THE SYSTEM SHALL permitir ingresar titulo, descripcion, fecha, hora y lugar. (POL-PE-MINIM-004, Art. 6 - Finalidad)
- **REQ-EVT-002**: WHEN el empleado completa el formulario de inscripcion THE SYSTEM SHALL registrar el consentimiento previo, expreso y demostrable (timestamp + version de politica) antes de tratar el dato. (POL-PE-CONSENT-001, Art. 5 - Consentimiento)
- **REQ-EVT-003**: WHEN el empleado se inscribe en un evento THE SYSTEM SHALL capturar el minimo de campos necesarios (nombre, area y correo corporativo). (POL-PE-MINIM-004, Art. 7 - Proporcionalidad)
- **REQ-EVT-004**: WHEN el empleado cancela su inscripcion THE SYSTEM SHALL actualizar el estado del registro y mantener la trazabilidad de quien se inscribio y cuando. (POL-PE-MINIM-004, Art. 8 - Calidad)
- **REQ-EVT-005**: WHEN el organizador solicita ver la lista de inscritos THE SYSTEM SHALL mostrar los registros de los eventos propios para el control de aforo. (POL-PE-MINIM-004, Art. 6 - Finalidad)
- **REQ-EVT-006**: WHERE el evento ha finalizado hace 90 dias THE SYSTEM SHALL aplicar un plazo de retencion con purga automatica de los datos de inscripcion. (POL-PE-MINIM-004, Art. 20 - Supresion)

## Normas cumplidas

| Policy Card | Articulo | Descripcion |
|---|---|---|
| POL-PE-MINIM-004 | Art. 6, 7, 8, 20 | Finalidad, proporcionalidad, calidad y retencion |
| POL-PE-CONSENT-001 | Art. 5 | Consentimiento para tratamiento de datos personales |
