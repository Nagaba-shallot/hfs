from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.security import generate_qr_token
from hospital_feedback_system.repositories.department import department_repository
from hospital_feedback_system.schemas.department import DepartmentCreate, DepartmentUpdate


def get_department(db: Session, department_id: int):
    department = department_repository.get(db, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department


def get_department_by_qr_token(db: Session, qr_code_token: str):
    return db.query(department_repository.model).filter_by(qr_code_token=qr_code_token).first()


def list_departments(db: Session, only_active: bool = False):
    query = db.query(department_repository.model)
    if only_active:
        query = query.filter_by(is_active=True)
    return query.all()


def create_department(db: Session, data: DepartmentCreate):
    existing = db.query(department_repository.model).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Department name already exists"
        )
    values = data.model_dump()
    values["qr_code_token"] = generate_qr_token()
    return department_repository.create(db, values)


def update_department(db: Session, department_id: int, data: DepartmentUpdate):
    department = get_department(db, department_id)
    return department_repository.update(db, department, data.model_dump(exclude_unset=True))


def rotate_qr_token(db: Session, department_id: int):
    department = get_department(db, department_id)
    return department_repository.update(db, department, {"qr_code_token": generate_qr_token()})


def delete_department(db: Session, department_id: int):
    department = get_department(db, department_id)
    department_repository.delete(db, department)