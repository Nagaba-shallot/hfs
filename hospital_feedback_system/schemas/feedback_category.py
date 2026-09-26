from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator
from hospital_feedback_system.core.constants import QuestionType


class FeedbackCategoryCreate(BaseModel):
    name: str
    display_order: int
    icon: str | None = None
    description: str | None = None
    department_id: int | None = None


class FeedbackCategoryUpdate(BaseModel):
    name: str | None = None
    display_order: int | None = None
    icon: str | None = None
    description: str | None = None
    department_id: int | None = None


class FeedbackCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feedback_category_id: int
    name: str
    department_id: int | None = None
    display_order: int
    icon: str | None = None
    description: str | None = None
    created_at: datetime

class SurveyQuestionInput(BaseModel):
    question_text: str
    question_type: QuestionType = "rating"
    order_in_feedback_category: int | None = None
    is_required: bool = True
    min_rating_label: str | None = None
    max_rating_label: str | None = None

    @model_validator(mode="after")
    def _strip_labels_on_non_rating(self):
        if self.question_type != "rating":
            self.min_rating_label = None
            self.max_rating_label = None
        return self


class SurveyCategoryInput(BaseModel):
    name: str
    display_order: int | None = None
    icon: str | None = None
    description: str | None = None
    department_id: int | None = None
    questions: list[SurveyQuestionInput] = []


class SurveyReplaceRequest(BaseModel):
    categories: list[SurveyCategoryInput]