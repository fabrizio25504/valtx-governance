---
id: FEAT-043
titulo: Expiración y renovación de consentimiento de ubicación
tags: [consentimiento, notificacion, pii, ubicacion, retencion]
policies: [POL-PE-CONSENT-001, POL-PE-MINIM-004, POL-PE-ARCO-005]
owner: producto@valtx.pe
estado: draft
---

# FEAT-043 · Expiración y renovación de consentimiento de ubicación

## Contexto
El consentimiento de geolocalización (FEAT-042) no es eterno: debe tener un plazo
y ser renovable. Este feature avisa al usuario antes de que expire, lo renueva de
forma demostrable, y **purga** los datos si no renueva. La Capa 0 activó (por triggers)
`POL-PE-CONSENT-001`, `POL-PE-MINIM-004` y `POL-PE-ARCO-005`.

## Requisitos (EARS) — cada uno cita la norma/principio que cumple

- **REQ-CONS-001** — WHEN el consentimiento de ubicación está a ≤ N días de expirar,
  THE SYSTEM SHALL notificar al usuario para que lo renueve.
  _Cumple: POL-PE-CONSENT-001 (Ley 29733 Art. 5) · PRIN-PRIV-001._

- **REQ-CONS-002** — WHERE el consentimiento expira sin renovación,
  THE SYSTEM SHALL detener la captura y purgar los datos de ubicación asociados.
  _Cumple: POL-PE-MINIM-004 (Ley 29733 Art. 8, 20) · POL-PE-ARCO-005._

- **REQ-CONS-003** — WHEN el usuario renueva el consentimiento,
  THE SYSTEM SHALL registrar la renovación con timestamp y versión de política.
  _Cumple: POL-PE-CONSENT-001 (consentimiento demostrable)._

## Normas cumplidas (trazable)
| REQ | Policy Card | Fuente (artículo) |
|-----|-------------|-------------------|
| REQ-CONS-001 | POL-PE-CONSENT-001 | Ley 29733 Art. 5 |
| REQ-CONS-002 | POL-PE-MINIM-004 · POL-PE-ARCO-005 | Ley 29733 Art. 8, 20, 22 |
| REQ-CONS-003 | POL-PE-CONSENT-001 | Ley 29733 Art. 5 |
