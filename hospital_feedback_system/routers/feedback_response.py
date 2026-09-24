from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin, get_current_patient
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.schemas.feedback_response import (
    FeedbackResponseCreate,
    FeedbackResponseRead,
)
from hospital_feedback_system.services import feedback_response as feedback_response_service

router = APIRouter(prefix="/feedback-responses", tags=["feedback-responses"])


@router.post("", response_model=FeedbackResponseRead, status_code=status.HTTP_201_CREATED)
def submit_answer(
    data: FeedbackResponseCreate,
    patient: Patients = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    return feedback_response_service.submit_answer(db, patient, data)


@router.get("/me", response_model=list[FeedbackResponseRead])
def read_my_answers(
    patient: Patients = Depends(get_current_patient), db: Session = Depends(get_db)
):
    return feedback_response_service.list_feedback_responses(db, patient_id=patient.patient_id)


@router.get("", response_model=list[FeedbackResponseRead])
def list_answers(
    patient_id: int | None = None,
    question_id: int | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return feedback_response_service.list_feedback_responses(db, patient_id, question_id)