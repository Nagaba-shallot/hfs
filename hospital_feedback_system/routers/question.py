from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from hospital_feedback_system.services import question as question_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionRead])
def list_questions(feedback_category_id: int | None = None, db: Session = Depends(get_db)):
    return question_service.list_questions(db, feedback_category_id)


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    return question_service.create_question(db, data)


@router.patch("/{question_id}", response_model=QuestionRead)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return question_service.update_question(db, question_id, data)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    question_service.delete_question(db, question_id)