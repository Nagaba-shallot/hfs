from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.survey_rules import answer_shape_error
from hospital_feedback_system.models.feedback_response import Feedback_response
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.models.question import Questions
from hospital_feedback_system.repositories.feedback_response import feedback_response_repository
from hospital_feedback_system.schemas.feedback_response import FeedbackResponseCreate
from hospital_feedback_system.services import survey_progress as survey_progress_service


def get_feedback_response(db: Session, feedback_response_id: int):
    response = feedback_response_repository.get(db, feedback_response_id)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")
    return response


def list_feedback_responses(
    db: Session, patient_id: int | None = None, question_id: int | None = None
):
    query = db.query(Feedback_response)
    if patient_id is not None:
        query = query.filter_by(patient_id=patient_id)
    if question_id is not None:
        query = query.filter_by(question_id=question_id)
    return query.order_by(Feedback_response.created_at.desc()).all()


def submit_answer(db: Session, patient: Patients, data: FeedbackResponseCreate):
    question = db.get(Questions, data.question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    error = answer_shape_error(
        question.question_type, data.rating_value, data.text_response, data.yes_no_value
    )
    if error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error)

    existing = (
        db.query(Feedback_response)
        .filter_by(patient_id=patient.patient_id, question_id=data.question_id)
        .first()
    )
    if existing:
        for field in ("rating_value", "text_response", "yes_no_value"):
            setattr(existing, field, getattr(data, field))
        db.commit()
        db.refresh(existing)
        response = existing
    else:
        response = feedback_response_repository.create(
            db, {**data.model_dump(), "patient_id": patient.patient_id}
        )

    survey_progress_service.recompute(db, patient.patient_id)
    return response