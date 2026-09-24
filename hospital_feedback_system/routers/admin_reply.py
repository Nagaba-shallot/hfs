from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hospital_feedback_system.core.deps import get_current_admin
from hospital_feedback_system.database import get_db
from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.schemas.admin_reply import (
    AdminReplyCreate,
    AdminReplyRead,
    AdminReplyUpdate,
)
from hospital_feedback_system.services import admin_reply as admin_reply_service

router = APIRouter(prefix="/admin-replies", tags=["admin-replies"])


@router.get("", response_model=list[AdminReplyRead])
def list_replies(
    feedback_response_id: int | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return admin_reply_service.list_admin_replies(db, feedback_response_id)


@router.post("", response_model=AdminReplyRead, status_code=status.HTTP_201_CREATED)
def create_reply(
    data: AdminReplyCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return admin_reply_service.create_admin_reply(db, admin, data)


@router.patch("/{admin_reply_id}", response_model=AdminReplyRead)
def update_reply(
    admin_reply_id: int,
    data: AdminReplyUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return admin_reply_service.update_admin_reply(db, admin_reply_id, data)


@router.delete("/{admin_reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reply(
    admin_reply_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    admin_reply_service.delete_admin_reply(db, admin_reply_id)