---
id: FEAT-053
titulo: Panel de estado de consentimiento del titular
tags: [cuenta, perfil, marketing, almacenamiento, cifrado]
policies: [POL-PE-ARCO-005, POL-PE-CONSENT-001, POL-PE-SEG-006, POL-PE-MINIM-004]
owner: producto@valtx.pe
estado: draft
module: src/panel_de_estado_de.py
---

# Feature Specification: Panel de estado de consentimiento del titular

**Feature Branch**: `053-panel-de-estado-de`

**Created**: 2023-10-25

**Status**: Draft

**Input**: User description: "Panel de estado de consentimiento del titular. Consulta el consentimiento vigente de un empleado a partir de su cuenta y devuelve un resumen con el estado actual, la fecha de otorgamiento y los canales aceptados. Permite revocar el consentimiento de marketing desde el mismo perfil, dejando constancia con cifrado en el almacenamiento."

## Contexto

El titular de los datos personales necesita transparencia y control sobre la información que ha autorizado a tratar. Actualmente, no existe un punto centralizado donde un empleado pueda verificar el estado de su consentimiento para distintos canales (especialmente marketing) ni ejercer su derecho a revocarlo. Este feature implementa un panel de consulta que devuelve un resumen claro del consentimiento vigente y permite la revocación directa, garantizando que toda acción quede registrada de forma segura mediante cifrado, cumpliendo con los principios de seguridad y los derechos ARCO.

## Requisitos (EARS)

- **REQ-PAN-001**: WHEN el titular solicita acceso a su panel de consentimiento THE SYSTEM SHALL devolver un resumen con el estado actual, la fecha de otorgamiento y los canales aceptados. (Cumple POL-PE-ARCO-005 Art. 19 - Derecho de acceso)
- **REQ-PAN-002**: WHEN el titular revoca el consentimiento de marketing desde su perfil THE SYSTEM SHALL actualizar el estado y registrar la acción dejando constancia con cifrado en el almacenamiento. (Cumple POL-PE-CONSENT-001 Art. 5 - Principio de consentimiento y revocabilidad)
- **REQ-PAN-003**: THE SYSTEM SHALL cifrar los registros de consentimiento y revocación en el almacenamiento en reposo. (Cumple POL-PE-SEG-006 Art. 16 - Seguridad del tratamiento)
- **REQ-PAN-004**: THE SYSTEM SHALL capturar el mínimo de campos necesarios para identificar la cuenta y el estado del canal de marketing. (Cumple POL-PE-MINIM-004 Art. 7 - Proporcionalidad y calidad)

## Normas cumplidas

| Policy Card | Principio | Requisito EARS |
|-------------|-----------|-----------------|
| POL-PE-ARCO-005 | PRIN-PRIV-001 | REQ-PAN-001 |
| POL-PE-CONSENT-001 | PRIN-PRIV-001 | REQ-PAN-002 |
| POL-PE-SEG-006 | PRIN-SEC-002 | REQ-PAN-003 |
| POL-PE-MINIM-004 | PRIN-PRIV-001 | REQ-PAN-004 |
