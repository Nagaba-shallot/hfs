from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from hospital_feedback_system.core.constants import QuestionType

_NAME_MAX = 120
_ICON_MAX = 50
_DESCRIPTION_MAX = 1000
_QUESTION_TEXT_MAX = 500
_RATING_LABEL_MAX = 50


class FeedbackCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=_NAME_MAX)
    display_order: int
    icon: str | None = Field(default=None, max_length=_ICON_MAX)
    description: str | None = Field(default=None, max_length=_DESCRIPTION_MAX)
    department_id: int | None = None


class FeedbackCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=_NAME_MAX)
    display_order: int | None = None
    icon: str | None = Field(default=None, max_length=_ICON_MAX)
    description: str | None = Field(default=None, max_length=_DESCRIPTION_MAX)
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
    question_text: str = Field(min_length=1, max_length=_QUESTION_TEXT_MAX)
    question_type: QuestionType = "rating"
    order_in_feedback_category: int | None = None
    is_required: bool = True
    min_rating_label: str | None = Field(default=None, max_length=_RATING_LABEL_MAX)
    max_rating_label: str | None = Field(default=None, max_length=_RATING_LABEL_MAX)

    @model_validator(mode="after")
    def _strip_labels_on_non_rating(self):
        if self.question_type != "rating":
            self.min_rating_label = None
            self.max_rating_label = None
        return self


class SurveyCategoryInput(BaseModel):
    name: str = Field(min_length=1, max_length=_NAME_MAX)
    display_order: int | None = None
    icon: str | None = Field(default=None, max_length=_ICON_MAX)
    description: str | None = Field(default=None, max_length=_DESCRIPTION_MAX)
    department_id: int | None = None
    questions: list[SurveyQuestionInput] = Field(default_factory=list, max_length=20)


class SurveyReplaceRequest(BaseModel):
    categories: list[SurveyCategoryInput] = Field(max_length=20)


class SurveyReplaceResult(BaseModel):
    categories_created: int
    questions_created: int
    categories_preserved: list[str]