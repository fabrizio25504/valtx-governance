---
id: FEAT-042
titulo: Check-in por geolocalización
tags: [ubicacion, geolocalizacion, gps, pii]
owner: producto@valtx.pe
estado: draft
---

# FEAT-042 · Check-in por geolocalización

## Contexto
El usuario hace "check-in" en un local capturando su ubicación. Toca datos
personales de geolocalización → la **Capa 0** activó las Policy Cards
`POL-PRIV-GEO-001` y `POL-DATA-RET-002`.

## Requisitos (EARS) — cada uno cita la norma/principio que cumple

- **REQ-GEO-001** — WHEN el usuario activa el check-in por ubicación,
  THE SYSTEM SHALL solicitar y registrar consentimiento explícito
  (timestamp + versión de política) antes de capturar coordenadas.
  _Cumple: POL-PRIV-GEO-001 (Ley 29733 art.5, 13.7) · PRIN-PRIV-001._

- **REQ-GEO-002** — THE SYSTEM SHALL almacenar la ubicación con un plazo de
  retención definido y purga automática al expirar.
  _Cumple: POL-DATA-RET-002 (Ley 29733 art.8)._

- **REQ-GEO-003** — WHERE el usuario revoca el consentimiento,
  THE SYSTEM SHALL detener la captura y purgar las coordenadas asociadas.
  _Cumple: POL-PRIV-GEO-001 (revocabilidad) · PRIN-PRIV-001._

## Normas cumplidas (trazable)
| REQ | Policy Card | Fuente | version_hash |
|-----|-------------|--------|--------------|
| REQ-GEO-001 | POL-PRIV-GEO-001 | Ley 29733 art.5,13.7 | 7402e776 |
| REQ-GEO-002 | POL-DATA-RET-002 | Ley 29733 art.8 | 77b0e410 |
| REQ-GEO-003 | POL-PRIV-GEO-001 | Ley 29733 art.13.7 | 7402e776 |
