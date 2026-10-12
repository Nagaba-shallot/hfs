from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hospital_feedback_system.models.department import Department
from hospital_feedback_system.models.feedback_response import Feedback_response
from hospital_feedback_system.models.question import Questions
from hospital_feedback_system.repositories.feedback_category import feedback_category_repository
from hospital_feedback_system.repositories.question import questions_repository
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


def _validate_department_id(db: Session, department_id: int | None) -> None:
    
    if department_id is None:
        return
    if db.get(Department, department_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department {department_id} does not exist",
        )


def create_feedback_category(db: Session, data: FeedbackCategoryCreate):
    _validate_department_id(db, data.department_id)
    return feedback_category_repository.create(db, data.model_dump())


def update_feedback_category(db: Session, feedback_category_id: int, data: FeedbackCategoryUpdate):
    feedback_category = get_feedback_category(db, feedback_category_id)
    changes = data.model_dump(exclude_unset=True)
    if "department_id" in changes:
        _validate_department_id(db, changes["department_id"])
    return feedback_category_repository.update(db, feedback_category, changes)


def delete_feedback_category(db: Session, feedback_category_id: int):
    feedback_category = get_feedback_category(db, feedback_category_id)
    try:
        feedback_category_repository.delete(db, feedback_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This category has patient responses recorded against it and can't be "
            "deleted. Remove or archive its questions individually if you need to retire it.",
        )


def _category_has_responses(db: Session, feedback_category_id: int) -> bool:
    return (
        db.query(Feedback_response.feedback_response_id)
        .join(Questions, Feedback_response.question_id == Questions.question_id)
        .filter(Questions.feedback_category_id == feedback_category_id)
        .first()
        is not None
    )


def replace_survey(db: Session, categories: list[dict]) -> dict:
    
    for cat in categories:
        _validate_department_id(db, cat.get("department_id"))

    existing = feedback_category_repository.get_all(db)
    preserved_names = []
    removable_ids = []
    for cat in existing:
        if _category_has_responses(db, cat.feedback_category_id):
            preserved_names.append(cat.name)
        else:
            removable_ids.append(cat.feedback_category_id)

    if removable_ids:
        db.query(feedback_category_repository.model).filter(
            feedback_category_repository.model.feedback_category_id.in_(removable_ids)
        ).delete(synchronize_session=False)
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
            created_questions += 1

    return {
        "categories_created": created_categories,
        "questions_created": created_questions,
        "categories_preserved": preserved_names,
    }