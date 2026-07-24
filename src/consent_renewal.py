"""
FEAT-043 · Expiración y renovación de consentimiento de ubicación.
Cada bloque cita su REQ (habilita el orphan-check). Funciones puras: el scheduler,
el canal de notificación y la purga se inyectan.

consent = {"user", "granted_at": epoch, "expires_at": epoch, "policy_version": str}
"""
import time

DAY = 86400


def days_until_expiry(consent, now=None):
    # REQ-CONS-001: base para el cálculo de proximidad de expiración
    now = time.time() if now is None else now
    return int((consent["expires_at"] - now) // DAY)


def needs_renewal_notice(consent, now=None, window_days=7):
    # REQ-CONS-001: avisar cuando faltan <= window_days y aún no expiró
    d = days_until_expiry(consent, now)
    return 0 <= d <= window_days


def expire_and_purge(consent, purge_fn, now=None):
    # REQ-CONS-002: si expiró sin renovación, detener captura y purgar
    now = time.time() if now is None else now
    if consent["expires_at"] <= now:
        purge_fn(consent["user"])
        return True
    return False


def renew(consent, policy_version, now=None, period_days=180):
    # REQ-CONS-003: registrar renovación demostrable (timestamp + versión)
    now = time.time() if now is None else now
    return {
        **consent,
        "policy_version": policy_version,
        "renewed_at": now,
        "expires_at": now + period_days * DAY,
    }
