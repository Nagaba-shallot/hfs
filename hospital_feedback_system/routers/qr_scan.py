from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.core.rate_limit import qr_scan_limiter
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.schemas.patients import PatientSession
from hospital_feedback_system.schemas.qr_scan import QRScanRead
from hospital_feedback_system.services import qr_scan as qr_scan_service

router = APIRouter(tags=["qr-scan"])


@router.post("/qr-scan/{qr_code_token}", response_model=PatientSession)
def scan(
    qr_code_token: str,
    request: Request,
    db: Session = Depends(get_db),
    _rate_limited: None = Depends(qr_scan_limiter),
):
    return qr_scan_service.record_scan_and_start_session(db, qr_code_token, request)


@router.get("/qr-scans", response_model=list[QRScanRead])
def list_scans(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return qr_scan_service.list_scans(db)