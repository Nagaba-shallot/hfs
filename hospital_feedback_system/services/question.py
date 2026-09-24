from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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


def create_question(db: Session, data: QuestionCreate):
    return questions_repository.create(db, data.model_dump())


def update_question(db: Session, question_id: int, data: QuestionUpdate):
    question = get_question(db, question_id)
    return questions_repository.update(db, question, data.model_dump(exclude_unset=True))


def delete_question(db: Session, question_id: int):
    question = get_question(db, question_id)
    questions_repository.delete(db, question)