from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator
from hospital_feedback_system.core.survey_rules import answer_shape_error


class FeedbackResponseCreate(BaseModel):
    question_id: int
    rating_value: int | None = None
    text_response: str | None = None
    yes_no_value: bool | None = None

    @model_validator(mode="after")
    def _exactly_one_value(self):
        provided = [
            v is not None for v in (self.rating_value, self.text_response, self.yes_no_value)
        ]
        if sum(provided) != 1:
            raise ValueError(
                "provide exactly one of rating_value, text_response, yes_no_value"
            )
        return self


class FeedbackResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feedback_response_id: int
    patient_id: int
    question_id: int
    rating_value: int | None = None
    text_response: str | None = None
    yes_no_value: bool | None = None
    created_at: datetime