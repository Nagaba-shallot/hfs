from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin, get_current_patient
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.schemas.patients import PatientsRead
from hospital_feedback_system.services import patients as patients_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientsRead)
def read_my_record(patient: Patients = Depends(get_current_patient)):
    return patient


@router.get("", response_model=list[PatientsRead])
def list_patients(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return patients_service.list_patients(db)


@router.get("/{patient_id}", response_model=PatientsRead)
def read_patient(
    patient_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    return patients_service.get_patient(db, patient_id)