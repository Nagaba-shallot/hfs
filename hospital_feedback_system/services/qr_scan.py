from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from hospital_feedback_system.config import settings
from hospital_feedback_system.core.security import generate_session_token, hash_session_token
from hospital_feedback_system.models.patients import Patients
from hospital_feedback_system.models.qr_scan import QR_scan
from hospital_feedback_system.services.department import get_department_by_qr_token


def record_scan_and_start_session(db: Session, qr_code_token: str, request: Request):
    department = get_department_by_qr_token(db, qr_code_token)
    if department is None or not department.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid QR code")

    raw_token = generate_session_token()
    patient = Patients(
        session_token=hash_session_token(raw_token),
        department_visited=department.name,
        is_anonymous=True,
    )
    db.add(patient)
    db.flush()  

    scan = QR_scan(
        qr_code_token=qr_code_token,
        department=department.name,
        patient_id=patient.patient_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(scan)
    db.commit()
    db.refresh(patient)

    return {
        "session_token": raw_token,
        "patient_id": patient.patient_id,
        "department_visited": patient.department_visited,
        "expires_in_hours": settings.PATIENT_SESSION_HOURS,
    }


def list_scans(db: Session):
    return db.query(QR_scan).order_by(QR_scan.scanned_at.desc()).all()