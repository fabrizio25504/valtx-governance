from datetime import datetime, timedelta

class EventCalendar:
    def __init__(self):
        self.events = {}  # REQ-EVT-001
        self.registrations = {}  # REQ-EVT-001
        self.policy_version = "1.0"  # REQ-EVT-002

    def create_event(self, event_id, title, description, date, time, place, organizer_id):
        self.events[event_id] = {  # REQ-EVT-001
            "title": title,  # REQ-EVT-001
            "description": description,  # REQ-EVT-001
            "date": date,  # REQ-EVT-001
            "time": time,  # REQ-EVT-001
            "place": place,  # REQ-EVT-001
            "organizer_id": organizer_id,  # REQ-EVT-001
            "status": "open"  # REQ-EVT-001
        }
        self.registrations[event_id] = []  # REQ-EVT-001

    def register_for_event(self, event_id, employee_id, name, area, corporate_email, consent_accepted):
        if not consent_accepted:  # REQ-EVT-002
            raise ValueError("Consent must be accepted to register")  # REQ-EVT-002
        
        registration = {  # REQ-EVT-003
            "employee_id": employee_id,  # REQ-EVT-004
            "name": name,  # REQ-EVT-003
            "area": area,  # REQ-EVT-003
            "corporate_email": corporate_email,  # REQ-EVT-003
            "consent": {  # REQ-EVT-002
                "accepted": True,  # REQ-EVT-002
                "timestamp": datetime.now().isoformat(),  # REQ-EVT-002
                "policy_version": self.policy_version  # REQ-EVT-002
            },
            "registered_at": datetime.now().isoformat(),  # REQ-EVT-004
            "status": "active"  # REQ-EVT-004
        }
        self.registrations[event_id].append(registration)  # REQ-EVT-003

    def cancel_registration(self, event_id, employee_id):
        for reg in self.registrations.get(event_id, []):  # REQ-EVT-004
            if reg["employee_id"] == employee_id and reg["status"] == "active":  # REQ-EVT-004
                reg["status"] = "cancelled"  # REQ-EVT-004
                reg["cancelled_at"] = datetime.now().isoformat()  # REQ-EVT-004
                break  # REQ-EVT-004

    def view_attendees(self, event_id, organizer_id):
        event = self.events.get(event_id)  # REQ-EVT-005
        if not event or event["organizer_id"] != organizer_id:  # REQ-EVT-005
            raise ValueError("Organizer can only view attendees of their own events")  # REQ-EVT-005
        return self.registrations.get(event_id, [])  # REQ-EVT-005

    def purge_old_event_data(self, current_date=None):
        if current_date is None:  # REQ-EVT-006
            current_date = datetime.now()  # REQ-EVT-006
        
        for event_id, event in list(self.events.items()):  # REQ-EVT-006
            event_date = datetime.fromisoformat(event["date"])  # REQ-EVT-006
            if (current_date - event_date).days > 90:  # REQ-EVT-006
                self.registrations[event_id] = []  # REQ-EVT-006
