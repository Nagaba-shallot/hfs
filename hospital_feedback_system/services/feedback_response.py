from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.survey_rules import answer_shape_error
from hospital_feedback_system.models.feedback_response import Feedback_response
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.models.question import Questions
from hospital_feedback_system.repositories.feedback_response import feedback_response_repository
from hospital_feedback_system.schemas.feedback_response import FeedbackResponseCreate
from hospital_feedback_system.services import survey_progress as survey_progress_service
from hospital_feedback_system.models.department import Department


def get_feedback_response(db: Session, feedback_response_id: int):
    response = feedback_response_repository.get(db, feedback_response_id)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")
    return response


def list_feedback_responses(
    db: Session, patient_id: int | None = None, question_id: int | None = None
):
    query = (
        db.query(
            Feedback_response,
            Department.name.label("department_name"),
        )
        .join(Patients, Patients.patient_id == Feedback_response.patient_id)
        .outerjoin(Department, Department.department_id == Patients.department_id)
    )
    if patient_id is not None:
        query = query.filter(Feedback_response.patient_id == patient_id)
    if question_id is not None:
        query = query.filter(Feedback_response.question_id == question_id)

    rows = query.order_by(Feedback_response.created_at.desc()).all()

    return [
        {
            "feedback_response_id": r.feedback_response_id,
            "patient_id": r.patient_id,
            "question_id": r.question_id,
            "rating_value": r.rating_value,
            "text_response": r.text_response,
            "yes_no_value": r.yes_no_value,
            "created_at": r.created_at,
            "department_name": department_name,
        }
        for r, department_name in rows
    ]

def submit_answer(db: Session, patient: Patients, data: FeedbackResponseCreate):
    question = db.get(Questions, data.question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    error = answer_shape_error(
        question.question_type, data.rating_value, data.text_response, data.yes_no_value
    )
    if error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error)

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