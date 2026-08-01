def run_retention_job(logs):
    # REQ-RET-001
    # Filter out expired logs to apply retention policy and purge vencidos
    return [log for log in logs if not log.get("is_expired", False)]

def export_access_history(user_id, history):
    # REQ-PORT-001
    # Filter history for the specific user and format it into a structured format
    user_history = [h for h in history if h.get("user_id") == user_id]
    
    structured_data = []
    for entry in user_history:
        structured_data.append({
            "timestamp": entry.get("timestamp"),
            "action": entry.get("action"),
            "ip_address": entry.get("ip_address"),
            "resource": entry.get("resource")
        })
        
    return structured_data
