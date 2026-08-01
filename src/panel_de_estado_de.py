import os
import json
from datetime import datetime
from cryptography.fernet import Fernet

# Mock database representing the consent records
_consent_db = {
    "user123": {
        "account": "user123",
        "status": "vigente",
        "grant_date": "2023-01-15",
        "accepted_channels": ["email", "sms"]
    }
}

# Mock storage for encrypted logs
_encrypted_storage = []

# Fallback solo para entornos sin CONSENT_ENCRYPTION_KEY (p.ej. tests): generada
# UNA vez por proceso. Antes se llamaba Fernet.generate_key() en cada invocación
# de _get_cipher(), así que cifrar y descifrar en el mismo proceso usaban claves
# distintas y la excepción disparaba siempre — save_encrypted_consent_record
# devolvía False incondicionalmente.
_FALLBACK_KEY = Fernet.generate_key()

def _get_cipher():
    # PRIN-SEC-002: Secrets must be read from environment variables, never hardcoded
    key = os.environ.get('CONSENT_ENCRYPTION_KEY')
    if not key:
        # Fallback for testing environments where key is not set
        key = _FALLBACK_KEY
    return Fernet(key)

def get_consent_summary(account):
    # REQ-PAN-001: WHEN el titular solicita acceso a su panel de consentimiento THE SYSTEM SHALL devolver un resumen con el estado actual, la fecha de otorgamiento y los canales aceptados.
    # POL-PE-ARCO-005: Cumple el derecho de acceso
    record = _consent_db.get(account)
    if not record:
        return {
            "account": account,
            "status": "no_encontrado",
            "grant_date": "",
            "accepted_channels": []
        }
    
    return {
        "account": record["account"],
        "status": record["status"],
        "grant_date": record["grant_date"],
        "accepted_channels": record["accepted_channels"]
    }

def revoke_marketing_consent(account):
    # REQ-PAN-002: WHEN el titular revoca el consentimiento de marketing desde su perfil THE SYSTEM SHALL actualizar el estado y registrar la acción dejando constancia con cifrado en el almacenamiento.
    # POL-PE-CONSENT-001: Cumple el principio de consentimiento y revocabilidad
    record = _consent_db.get(account)
    if not record:
        return {
            "account": account,
            "new_status": "no_encontrado",
            "encrypted_log_id": ""
        }
    
    # Update status to revoked
    record["status"] = "revocado"
    if "email" in record["accepted_channels"]:
        record["accepted_channels"].remove("email")
    if "sms" in record["accepted_channels"]:
        record["accepted_channels"].remove("sms")
    
    # Create and save the log — EN CLARO: save_encrypted_consent_record es quien cifra.
    log_data = {
        "action": "revoke_marketing",
        "account": account,
        "timestamp": datetime.now().isoformat()
    }
    record_id = f"rec-{len(_encrypted_storage) + 1}"
    entry = {
        "record_id": record_id,
        "payload": json.dumps(log_data)
    }
    save_encrypted_consent_record(entry)
    
    return {
        "account": account,
        "new_status": record["status"],
        "encrypted_log_id": record_id
    }

def save_encrypted_consent_record(entry):
    # REQ-PAN-003: THE SYSTEM SHALL cifrar los registros de consentimiento y revocación
    # en el almacenamiento en reposo. `entry["payload"]` llega EN CLARO — cifrarlo es
    # responsabilidad de ESTA función, no de quien la llama (ver contracts.yaml).
    # POL-PE-SEG-006: Cumple la seguridad del tratamiento
    try:
        encrypted_data = _get_cipher().encrypt(entry["payload"].encode()).decode()
    except Exception:
        return False
    _encrypted_storage.append({"record_id": entry["record_id"], "encrypted_data": encrypted_data})
    return True

def verify_minimization_fields(account, marketing_status):
    # REQ-PAN-004: THE SYSTEM SHALL capturar el mínimo de campos necesarios para identificar la cuenta y el estado del canal de marketing.
    # POL-PE-MINIM-004: Cumple la proporcionalidad y calidad
    return {
        "account": account,
        "marketing_status": marketing_status
    }
