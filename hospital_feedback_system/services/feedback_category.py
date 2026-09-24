from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.repositories.feedback_category import feedback_category_repository
from hospital_feedback_system.schemas.feedback_category import (
    FeedbackCategoryCreate,
    FeedbackCategoryUpdate,
)


def get_feedback_category(db: Session, feedback_category_id: int):
    feedback_category = feedback_category_repository.get(db, feedback_category_id)
    if not feedback_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback category not found"
        )
    return feedback_category


def list_feedback_categories(db: Session):
    return (
        db.query(feedback_category_repository.model)
        .order_by(feedback_category_repository.model.display_order)
        .all()
    )


def create_feedback_category(db: Session, data: FeedbackCategoryCreate):
    return feedback_category_repository.create(db, data.model_dump())


def update_feedback_category(db: Session, feedback_category_id: int, data: FeedbackCategoryUpdate):
    feedback_category = get_feedback_category(db, feedback_category_id)
    return feedback_category_repository.update(
        db, feedback_category, data.model_dump(exclude_unset=True)
    )


def delete_feedback_category(db: Session, feedback_category_id: int):
    feedback_category = get_feedback_category(db, feedback_category_id)
    feedback_category_repository.delete(db, feedback_category)