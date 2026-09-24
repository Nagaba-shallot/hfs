from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SurveyProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    survey_progress_id: int
    patient_id: int
    current_feedback_category_order: int
    is_completed: bool
    total_questions_answered: int
    completed_at: datetime | None = None
    last_activity_at: datetime