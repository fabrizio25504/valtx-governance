from pytest_bdd import scenarios, given, when, then
from src.panel_de_estado_de import (
    get_consent_summary,
    revoke_marketing_consent,
    save_encrypted_consent_record,
    verify_minimization_fields,
    _encrypted_storage,
)

scenarios("../panel-de-estado-de.feature")

state = {}

@given('un empleado con cuenta "user123" que tiene un consentimiento vigente')
def setup_active_consent():
    state["account"] = "user123"
    state["expected_status"] = "vigente"
    state["expected_date"] = "2023-01-15"
    state["expected_channels"] = ["email", "sms"]

@when('solicita el resumen de su consentimiento')
def request_summary():
    state["summary_result"] = get_consent_summary(state["account"])

@then('el sistema devuelve un resumen con el estado "vigente"')
def check_summary_status():
    assert state["summary_result"]["status"] == state["expected_status"]

@then('la fecha de otorgamiento "2023-01-15"')
def check_summary_date():
    assert state["summary_result"]["grant_date"] == state["expected_date"]

@then('los canales aceptados ["email", "sms"]')
def check_summary_channels():
    assert state["summary_result"]["accepted_channels"] == state["expected_channels"]

@given('un empleado con cuenta "user123" que tiene un consentimiento vigente para marketing')
def setup_marketing_consent():
    state["account"] = "user123"

@when('revoca el consentimiento de marketing desde su perfil')
def perform_revocation():
    state["revocation_result"] = revoke_marketing_consent(state["account"])

@then('el sistema actualiza el estado del consentimiento a "revocado"')
def check_revocation_status():
    assert state["revocation_result"]["new_status"] == "revocado"

@then('registra la acción de revocación con cifrado en el almacenamiento')
def check_revocation_log():
    assert state["revocation_result"]["encrypted_log_id"] != ""

@given('un sistema que almacena registros de consentimiento')
def setup_storage_system():
    # Dato literal EN CLARO — cifrarlo es responsabilidad de save_encrypted_consent_record
    # (REQ-PAN-003 dice "THE SYSTEM SHALL cifrar"), no de este fixture.
    state["plaintext_payload"] = "consent-log-payload"
    state["record_id"] = "rec-001"
    state["entry"] = {
        "record_id": state["record_id"],
        "payload": state["plaintext_payload"],
    }

@when('se guarda un nuevo registro de consentimiento o revocación')
def perform_save_record():
    state["save_result"] = save_encrypted_consent_record(state["entry"])

@then('el sistema persiste el registro aplicando cifrado en reposo')
def check_persisted_encrypted():
    assert state["save_result"] is True
    stored = [r for r in _encrypted_storage if r["record_id"] == state["record_id"]]
    assert stored, "no se encontró el registro persistido en el almacenamiento"
    encrypted_data = stored[-1]["encrypted_data"]
    # Un cifrador no-op (que devuelve el dato tal cual) tiene que hacer FALLAR
    # este assert — si no, el escenario no verifica que se haya cifrado nada.
    assert encrypted_data != state["plaintext_payload"], "lo persistido es igual al texto en claro — no se cifró"
    assert state["plaintext_payload"] not in encrypted_data, "el texto en claro aparece dentro de lo persistido"

@given('un empleado que accede al panel de consentimiento')
def setup_employee_access():
    state["account"] = "user456"
    state["marketing_status"] = "vigente"

@when('el sistema procesa la solicitud de visualización')
def process_visualization_request():
    state["minimization_result"] = verify_minimization_fields(
        state["account"], 
        state["marketing_status"]
    )

@then('el sistema captura unicamente la cuenta y el estado del canal de marketing')
def check_minimized_fields():
    result = state["minimization_result"]
    assert "account" in result
    assert "marketing_status" in result
    assert len(result) == 2
