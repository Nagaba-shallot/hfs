from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.repositories.feedback_category import feedback_category_repository
from hospital_feedback_system.schemas.feedback_category import (
    FeedbackCategoryCreate,
    FeedbackCategoryUpdate,
)
from hospital_feedback_system.repositories.question import questions_repository
from hospital_feedback_system.schemas.question import QuestionCreate


def get_feedback_category(db: Session, feedback_category_id: int):
    feedback_category = feedback_category_repository.get(db, feedback_category_id)
    if not feedback_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback category not found"
        )
    return feedback_category


def list_feedback_categories(db: Session, department_id: int | None = None):
    model = feedback_category_repository.model
    query = db.query(model)
    if department_id is not None:
        query = query.filter(
            (model.department_id == department_id) | (model.department_id.is_(None))
        )
    else:
        query = query.filter(model.department_id.is_(None))
    return query.order_by(model.display_order).all()


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

def replace_survey(db: Session, categories: list[dict]) -> dict:
    db.query(feedback_category_repository.model).delete(synchronize_session=False)
    db.commit()

    created_categories = 0
    created_questions = 0

    for cat in categories:
        category_row = feedback_category_repository.create(
            db,
            {
                "name": cat["name"],
                "display_order": cat.get("display_order", created_categories + 1),
                "icon": cat.get("icon"),
                "description": cat.get("description"),
                "department_id": cat.get("department_id"),
            },
        )
        created_categories += 1

        for i, q in enumerate(cat.get("questions", []), start=1):
            qd = q.model_dump() if hasattr(q, "model_dump") else q
            questions_repository.create(
                db,
                {
                    "feedback_category_id": category_row.feedback_category_id,
                    "question_text": qd["question_text"],
                    "question_type": qd["question_type"],
                    "order_in_feedback_category": qd.get("order_in_feedback_category") or i,
                    "is_required": qd.get("is_required", True),
                    "min_rating_label": qd.get("min_rating_label"),
                    "max_rating_label": qd.get("max_rating_label"),
                },
            )

    return {"categories": created_categories, "questions": created_questions}