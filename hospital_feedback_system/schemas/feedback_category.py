from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FeedbackCategoryCreate(BaseModel):
    name: str
    display_order: int
    icon: str | None = None
    description: str | None = None


class FeedbackCategoryUpdate(BaseModel):
    name: str | None = None
    display_order: int | None = None
    icon: str | None = None
    description: str | None = None


class FeedbackCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feedback_category_id: int
    name: str
    display_order: int
    icon: str | None = None
    description: str | None = None
    created_at: datetime