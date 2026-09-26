from typing import Literal

from pydantic import BaseModel, Field

QUESTION_TYPE_RATING = "rating"
QUESTION_TYPE_TEXT = "text"
QUESTION_TYPE_YES_NO = "yes_no"
QuestionType = Literal["rating", "text", "yes_no"]

MAX_CATEGORIES = 6
MAX_QUESTIONS_PER_CATEGORY = 6


class SurveyGenerateRequest(BaseModel):
    focus: str = Field(
        min_length=3,
        max_length=300,
        description="What to focus the survey on, e.g. 'Maternity Ward - staff "
        "communication and cleanliness'",
    )
    num_categories: int = Field(default=3, ge=1, le=MAX_CATEGORIES)
    questions_per_category: int = Field(default=3, ge=1, le=MAX_QUESTIONS_PER_CATEGORY)


class DraftQuestion(BaseModel):
    question_text: str
    question_type: QuestionType
    is_required: bool = True
    min_rating_label: str | None = None
    max_rating_label: str | None = None


class DraftCategory(BaseModel):
    name: str
    display_order: int
    icon: str | None = None
    questions: list[DraftQuestion]


class SurveyDraft(BaseModel):
    categories: list[DraftCategory]