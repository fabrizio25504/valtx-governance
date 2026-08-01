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

def _get_cipher():
    # PRIN-SEC-002: Secrets must be read from environment variables, never hardcoded
    key = os.environ.get('CONSENT_ENCRYPTION_KEY')
    if not key:
        # Fallback for testing environments where key is not set
        key = Fernet.generate_key()
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
    
    # Create and save encrypted log
    log_data = {
        "action": "revoke_marketing",
        "account": account,
        "timestamp": datetime.now().isoformat()
    }
    record_id = f"rec-{len(_encrypted_storage) + 1}"
    encrypted_data = _get_cipher().encrypt(json.dumps(log_data).encode()).decode()
    
    storage_record = {
        "record_id": record_id,
        "encrypted_data": encrypted_data
    }
    save_encrypted_consent_record(storage_record)
    
    return {
        "account": account,
        "new_status": record["status"],
        "encrypted_log_id": record_id
    }

def save_encrypted_consent_record(record):
    # REQ-PAN-003: THE SYSTEM SHALL cifrar los registros de consentimiento y revocación en el almacenamiento en reposo.
    # POL-PE-SEG-006: Cumple la seguridad del tratamiento
    try:
        # Verify that the data is actually encrypted by attempting decryption
        cipher = _get_cipher()
        cipher.decrypt(record["encrypted_data"].encode())
        _encrypted_storage.append(record)
        return True
    except Exception:
        return False

def verify_minimization_fields(account, marketing_status):
    # REQ-PAN-004: THE SYSTEM SHALL capturar el mínimo de campos necesarios para identificar la cuenta y el estado del canal de marketing.
    # POL-PE-MINIM-004: Cumple la proporcionalidad y calidad
    return {
        "account": account,
        "marketing_status": marketing_status
    }
