from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin, get_current_patient
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.schemas.survey_progress import SurveyProgressRead
from hospital_feedback_system.services import survey_progress as survey_progress_service

router = APIRouter(prefix="/survey-progress", tags=["survey-progress"])


@router.get("/me", response_model=SurveyProgressRead)
def read_my_progress(
    patient: Patients = Depends(get_current_patient), db: Session = Depends(get_db)
):
    return survey_progress_service.get_or_create(db, patient.patient_id)


@router.get("/{patient_id}", response_model=SurveyProgressRead)
def read_progress(
    patient_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    return survey_progress_service.get_or_create(db, patient_id)