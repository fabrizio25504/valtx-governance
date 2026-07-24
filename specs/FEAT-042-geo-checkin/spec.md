---
id: FEAT-042
titulo: Check-in por geolocalización
tags: [ubicacion, geolocalizacion, gps, pii]
policies: [POL-PE-CONSENT-001, POL-PE-UBIC-003, POL-PE-MINIM-004, POL-PE-ARCO-005]
owner: producto@valtx.pe
estado: draft
---

# FEAT-042 · Check-in por geolocalización

## Contexto
El usuario hace "check-in" en un local capturando su ubicación. Toca datos
personales de geolocalización → la **Capa 0** activó (por triggers) las Policy Cards
`POL-PE-CONSENT-001`, `POL-PE-UBIC-003`, `POL-PE-MINIM-004`.

## Requisitos (EARS) — cada uno cita la norma/principio que cumple

- **REQ-GEO-001** — WHEN el usuario activa el check-in por ubicación,
  THE SYSTEM SHALL solicitar y registrar consentimiento previo, expreso y demostrable
  (timestamp + versión de política) antes de capturar coordenadas.
  _Cumple: POL-PE-CONSENT-001 (Ley 29733 Art. 5) · POL-PE-UBIC-003 · PRIN-PRIV-001._

- **REQ-GEO-002** — THE SYSTEM SHALL almacenar la ubicación con un plazo de
  retención definido y purga automática al expirar.
  _Cumple: POL-PE-MINIM-004 (Ley 29733 Art. 6-8, 20)._

- **REQ-GEO-003** — WHERE el usuario revoca el consentimiento,
  THE SYSTEM SHALL detener la captura y purgar las coordenadas asociadas.
  _Cumple: POL-PE-UBIC-003 (revocabilidad) · POL-PE-ARCO-005 (oposición) · PRIN-PRIV-001._

## Normas cumplidas (trazable)
| REQ | Policy Card | Fuente (artículo) |
|-----|-------------|-------------------|
| REQ-GEO-001 | POL-PE-CONSENT-001 · POL-PE-UBIC-003 | Ley 29733 Art. 5, 13 |
| REQ-GEO-002 | POL-PE-MINIM-004 | Ley 29733 Art. 6-8, 20 |
| REQ-GEO-003 | POL-PE-UBIC-003 · POL-PE-ARCO-005 | Ley 29733 Art. 20, 22 |
