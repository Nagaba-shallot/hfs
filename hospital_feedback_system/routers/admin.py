from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.constants import ROLE_SUPER_ADMIN
from hospital_feedback_system.core.deps import get_current_admin, require_role
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.schemas.admin import AdminCreate, AdminRead, AdminSelfUpdate, AdminUpdate, AdminPasswordChange
from hospital_feedback_system.services import admin as admin_service
from hospital_feedback_system.core.security import hash_password
from hospital_feedback_system.repositories.admin import admin_repository
from fastapi import HTTPException

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("", response_model=list[AdminRead], dependencies=[Depends(require_role(ROLE_SUPER_ADMIN))])
def list_admins(db: Session = Depends(get_db)):
    return admin_service.list_admins(db)


@router.post(
    "",
    response_model=AdminRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_SUPER_ADMIN))],
)
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter_by(email=data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    values = data.model_dump()
    values["password"] = hash_password(values.pop("password"))
    values["role"] = "admin"
    values["is_active"] = True
    return admin_repository.create(db, values)


@router.get("/me", response_model=AdminRead)
def read_my_profile(admin: Admin = Depends(get_current_admin)):
    return admin


@router.patch("/me", response_model=AdminRead)
def update_my_profile(
    data: AdminSelfUpdate,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return admin_service.update_admin_self(db, admin.admin_id, data)


@router.get(
    "/{admin_id}",
    response_model=AdminRead,
    dependencies=[Depends(require_role(ROLE_SUPER_ADMIN))],
)
def read_admin(admin_id: int, db: Session = Depends(get_db)):
    return admin_service.get_admin(db, admin_id)


@router.patch(
    "/{admin_id}",
    response_model=AdminRead,
    dependencies=[Depends(require_role(ROLE_SUPER_ADMIN))],
)
def update_admin(admin_id: int, data: AdminUpdate, db: Session = Depends(get_db)):
    return admin_service.update_admin_as_super(db, admin_id, data)

@router.patch("/me/password")
def change_my_password(
    payload: AdminPasswordChange,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        admin_service.change_password(
            db,
            admin,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "message": "Password changed. Please log in again."}

@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_SUPER_ADMIN))],
)
def delete_admin(
    admin_id: int,
    acting_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if admin_id == acting_admin.admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account"
        )
    admin_service.delete_admin(db, admin_id)