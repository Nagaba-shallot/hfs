from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class PatientsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: int
    phone_number: str | None = None
    department_visited: str
    visit_date: date | None = None
    is_anonymous: bool
    created_at: datetime

class PatientSession(BaseModel):
    session_token: str
    patient_id: int
    department_visited: str
    expires_in_hours: int