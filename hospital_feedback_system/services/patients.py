from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.repositories.patients import patients_repository


def get_patient(db: Session, patient_id: int):
    patient = patients_repository.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


def list_patients(db: Session):
    return patients_repository.get_all(db)