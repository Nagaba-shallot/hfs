from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator
from hospital_feedback_system.core.constants import QuestionType

class QuestionCreate(BaseModel):
    feedback_category_id: int
    question_text: str
    question_type: QuestionType = "rating"
    order_in_feedback_category: int
    is_required: bool = True
    min_rating_label: str | None = None
    max_rating_label: str | None = None

    @model_validator(mode="after")
    def _rating_labels_only_for_rating(self):
        if self.question_type != "rating" and (self.min_rating_label or self.max_rating_label):
            raise ValueError("rating labels only apply to question_type='rating'")
        return self

class QuestionUpdate(BaseModel):
    feedback_category_id: int | None = None
    question_text: str | None = None
    question_type: QuestionType | None = None
    order_in_feedback_category: int | None = None
    is_required: bool | None = None
    min_rating_label: str | None = None
    max_rating_label: str | None = None

class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: int
    feedback_category_id: int
    question_text: str
    question_type: str
    order_in_feedback_category: int
    is_required: bool
    min_rating_label: str | None = None
    max_rating_label: str | None = None
    created_at: datetime