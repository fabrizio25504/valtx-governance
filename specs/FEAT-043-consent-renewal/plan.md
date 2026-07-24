# Plan técnico — FEAT-043

## Enfoque
Módulo `src/consent_renewal.py` con funciones puras (sin I/O real; el scheduler y
el canal de notificación se inyectan). Se apoya en el registro de consentimiento de
FEAT-042 (`POL-PRIV-GEO`/`POL-PE-CONSENT-001`).

## Superficie
- `days_until_expiry(consent, today)` → int
- `needs_renewal_notice(consent, today, window_days)` → bool — REQ-CONS-001
- `expire_and_purge(consent, today, purge_fn)` → bool — REQ-CONS-002
- `renew(consent, policy_version, now)` → dict — REQ-CONS-003

## Contrato
`consent = {"user","granted_at","expires_at","policy_version"}`

## Validación
- Gherkin en `consent-renewal.feature` (@REQ-CONS-001/002/003).
- Gates: vigencia normativa · trazabilidad · cobertura 100%.
