"""
Implementación demo de FEAT-042. Cada bloque cita su REQ (habilita el orphan-check).
NOTA: contiene 2 problemas SEMBRADOS para que el gate los detecte:
  - una cita a REQ-GEO-009 (no existe en el spec)  -> alucinación
  - una línea sustantiva sin cita REQ               -> gap de trazabilidad
"""
import time


def request_consent(user, scope):
    # REQ-GEO-001: consentimiento explícito registrado antes de capturar
    record = {"user": user, "scope": scope, "ts": time.time(), "policy": "POL-PRIV-GEO-001"}
    return record


def capture_location(user, consent):
    # REQ-GEO-001: no capturar sin consentimiento válido
    if not consent:
        raise PermissionError("sin consentimiento")
    coords = _read_gps(user)
    return coords


def store_location(user, coords, retention_days=30):
    # REQ-GEO-002: retención con purga automática
    expires = time.time() + retention_days * 86400
    return {"user": user, "coords": coords, "expires_at": expires}


def revoke(user):
    # REQ-GEO-003: revocar detiene captura y purga coordenadas
    _purge(user)
    return True


def _read_gps(user):
    return (-12.0464, -77.0428)  # REQ-GEO-001: lectura de coordenadas


def _purge(user):
    return None  # REQ-GEO-003: purga de coordenadas
