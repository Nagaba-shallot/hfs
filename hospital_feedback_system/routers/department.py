from fastapi import APIRouter, Depends, status

from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.schemas.department import (
    DepartmentCreate,
    DepartmentQRToken,
    DepartmentRead,
    DepartmentUpdate,
)
from hospital_feedback_system.services import department as department_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    return department_service.list_departments(db, only_active=True)


@router.get("/all", response_model=list[DepartmentRead])
def list_all_departments(
    db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    return department_service.list_departments(db, only_active=False)


@router.post("", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    return department_service.create_department(db, data)


@router.patch("/{department_id}", response_model=DepartmentRead)
def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return department_service.update_department(db, department_id, data)


@router.get("/{department_id}/qr-token", response_model=DepartmentQRToken)
def get_qr_token(
    department_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    department = department_service.get_department(db, department_id)
    return DepartmentQRToken(
        department_id=department.department_id,
        qr_code_token=department.qr_code_token,
        scan_url_path=f"/qr-scan/{department.qr_code_token}",
    )


@router.post("/{department_id}/qr-token/rotate", response_model=DepartmentQRToken)
def rotate_qr_token(
    department_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    department = department_service.rotate_qr_token(db, department_id)
    return DepartmentQRToken(
        department_id=department.department_id,
        qr_code_token=department.qr_code_token,
        scan_url_path=f"/qr-scan/{department.qr_code_token}",
    )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    department_service.delete_department(db, department_id)