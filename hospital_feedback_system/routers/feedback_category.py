from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.schemas.feedback_category import (
    FeedbackCategoryCreate,
    FeedbackCategoryRead,
    FeedbackCategoryUpdate,
)
from hospital_feedback_system.services import feedback_category as feedback_category_service

router = APIRouter(prefix="/feedback-categories", tags=["feedback-categories"])


@router.get("", response_model=list[FeedbackCategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return feedback_category_service.list_feedback_categories(db)


@router.post("", response_model=FeedbackCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    data: FeedbackCategoryCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return feedback_category_service.create_feedback_category(db, data)


@router.patch("/{feedback_category_id}", response_model=FeedbackCategoryRead)
def update_category(
    feedback_category_id: int,
    data: FeedbackCategoryUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return feedback_category_service.update_feedback_category(db, feedback_category_id, data)


@router.delete("/{feedback_category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    feedback_category_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    feedback_category_service.delete_feedback_category(db, feedback_category_id)