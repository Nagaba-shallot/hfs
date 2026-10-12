from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hospital_feedback_system.models.feedback_category import Feedback_category
from hospital_feedback_system.repositories.question import questions_repository
from hospital_feedback_system.schemas.question import QuestionCreate, QuestionUpdate


def get_question(db: Session, question_id: int):
    question = questions_repository.get(db, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question


def list_questions(db: Session, feedback_category_id: int | None = None):
    query = db.query(questions_repository.model)
    if feedback_category_id is not None:
        query = query.filter_by(feedback_category_id=feedback_category_id)
    return query.order_by(questions_repository.model.order_in_feedback_category).all()


def _validate_category_id(db: Session, feedback_category_id: int) -> None:
    if db.get(Feedback_category, feedback_category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback category {feedback_category_id} does not exist",
        )


def create_question(db: Session, data: QuestionCreate):
    _validate_category_id(db, data.feedback_category_id)
    return questions_repository.create(db, data.model_dump())


def update_question(db: Session, question_id: int, data: QuestionUpdate):
    question = get_question(db, question_id)
    changes = data.model_dump(exclude_unset=True)
    if "feedback_category_id" in changes:
        _validate_category_id(db, changes["feedback_category_id"])
    return questions_repository.update(db, question, changes)


def delete_question(db: Session, question_id: int):
    question = get_question(db, question_id)
    try:
        questions_repository.delete(db, question)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This question has patient responses recorded against it and can't be "
            "deleted.",
        )