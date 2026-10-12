from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from hospital_feedback_system.core.constants import QuestionType

_QUESTION_TEXT_MAX = 500
_RATING_LABEL_MAX = 50


class QuestionCreate(BaseModel):
    feedback_category_id: int
    question_text: str = Field(min_length=1, max_length=_QUESTION_TEXT_MAX)
    question_type: QuestionType = "rating"
    order_in_feedback_category: int
    is_required: bool = True
    min_rating_label: str | None = Field(default=None, max_length=_RATING_LABEL_MAX)
    max_rating_label: str | None = Field(default=None, max_length=_RATING_LABEL_MAX)

    @model_validator(mode="after")
    def _rating_labels_only_for_rating(self):
        if self.question_type != "rating" and (self.min_rating_label or self.max_rating_label):
            raise ValueError("rating labels only apply to question_type='rating'")
        return self


class QuestionUpdate(BaseModel):
    feedback_category_id: int | None = None
    question_text: str | None = Field(default=None, min_length=1, max_length=_QUESTION_TEXT_MAX)
    question_type: QuestionType | None = None
    order_in_feedback_category: int | None = None
    is_required: bool | None = None
    min_rating_label: str | None = Field(default=None, max_length=_RATING_LABEL_MAX)
    max_rating_label: str | None = Field(default=None, max_length=_RATING_LABEL_MAX)


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