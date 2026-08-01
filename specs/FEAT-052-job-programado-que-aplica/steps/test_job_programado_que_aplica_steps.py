from pytest_bdd import scenarios, given, when, then
from src.job_programado_que_aplica import run_retention_job, export_access_history

scenarios("../job-programado-que-aplica.feature")

state = {}

@given("que existen logs de acceso con fechas de retención vencidas")
def setup_expired_logs():
    state["logs"] = [
        {"id": 1, "user": "user1", "date": "2023-01-01", "expired": True},
        {"id": 2, "user": "user2", "date": "2023-10-20", "expired": False}
    ]

@when("el job programado se ejecuta")
def execute_job():
    state["result"] = run_retention_job(state["logs"])

@then("el sistema purga los registros de logs vencidos")
def verify_purge():
    purged_logs = state["result"]
    assert purged_logs == [{"id": 2, "user": "user2", "date": "2023-10-20", "expired": False}]

@given("que el titular solicita exportar su historial de accesos desde su perfil")
def setup_export_request():
    state["user_id"] = "user1"
    state["history"] = [
        {"id": 1, "user": "user1", "date": "2023-10-21", "action": "login"}
    ]

@when("el sistema procesa la solicitud de exportación")
def process_export():
    state["export_result"] = export_access_history(state["user_id"], state["history"])

@then("el sistema entrega los datos de acceso en un formato estructurado")
def verify_export():
    export_data = state["export_result"]
    assert export_data == [{"id": 1, "user": "user1", "date": "2023-10-21", "action": "login"}]
