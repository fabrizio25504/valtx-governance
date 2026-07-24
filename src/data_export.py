import json  # REQ-EXP-001

def export_user_data(user_data):  # REQ-EXP-001
    """Generates a JSON file with user personal data."""
    file_name = f"{user_data['id']}_data_export.json"  # REQ-EXP-001
    with open(file_name, 'w') as json_file:  # REQ-EXP-001
        json.dump(user_data, json_file)  # REQ-EXP-001
    return file_name  # REQ-EXP-001

def calculate_deadline(request_date):  # REQ-EXP-002
    """Calculates the legal deadline for data export response."""
    from datetime import timedelta  # REQ-EXP-002
    deadline = request_date + timedelta(days=10)  # REQ-EXP-002
    return deadline  # REQ-EXP-002

if __name__ == "__main__":  # REQ-EXP-001
    # Example usage
    user_data_example = {  # REQ-EXP-001
        "id": 123,  # REQ-EXP-001
        "name": "John Doe",  # REQ-EXP-001
        "email": "john.doe@example.com"  # REQ-EXP-001
    }  # REQ-EXP-001
    export_user_data(user_data_example)  # REQ-EXP-001
