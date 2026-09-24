from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.security import hash_password, verify_password
from hospital_feedback_system.repositories.admin import admin_repository
from hospital_feedback_system.schemas.admin import AdminSelfUpdate, AdminUpdate


def get_admin(db: Session, admin_id: int):
    admin = admin_repository.get(db, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin


def list_admins(db: Session):
    return admin_repository.get_all(db)


def update_admin_self(db: Session, admin_id: int, data: AdminSelfUpdate):
    admin = get_admin(db, admin_id)
    changes = data.model_dump(exclude_unset=True)
    if "password" in changes:
        changes["password"] = hash_password(changes["password"])
    return admin_repository.update(db, admin, changes)


def update_admin_as_super(db: Session, admin_id: int, data: AdminUpdate):
    admin = get_admin(db, admin_id)
    return admin_repository.update(db, admin, data.model_dump(exclude_unset=True))


def delete_admin(db: Session, admin_id: int):
    admin = get_admin(db, admin_id)
    admin_repository.delete(db, admin)

def change_password(db, admin, current_password: str, new_password: str):
    if not verify_password(current_password, admin.password):
        raise ValueError("Current password is incorrect")
    admin.password = hash_password(new_password)
    admin.token_version += 1   
    db.commit()
    db.refresh(admin)
    return admin