from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hospital_feedback_system.models.admin import Admin
from hospital_feedback_system.models.feedback_response import Feedback_response
from hospital_feedback_system.repositories.admin_reply import admin_reply_repository
from hospital_feedback_system.schemas.admin_reply import AdminReplyCreate, AdminReplyUpdate


def get_admin_reply(db: Session, admin_reply_id: int):
    admin_reply = admin_reply_repository.get(db, admin_reply_id)
    if not admin_reply:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found")
    return admin_reply


def list_admin_replies(db: Session, feedback_response_id: int | None = None):
    query = db.query(admin_reply_repository.model)
    if feedback_response_id is not None:
        query = query.filter_by(feedback_response_id=feedback_response_id)
    return query.all()


def create_admin_reply(db: Session, admin: Admin, data: AdminReplyCreate):
    response = db.get(Feedback_response, data.feedback_response_id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback response not found"
        )
    values = data.model_dump()
    values["admin_id"] = admin.admin_id
    return admin_reply_repository.create(db, values)


def update_admin_reply(db: Session, admin_reply_id: int, data: AdminReplyUpdate):
    admin_reply = get_admin_reply(db, admin_reply_id)
    return admin_reply_repository.update(db, admin_reply, data.model_dump(exclude_unset=True))


def delete_admin_reply(db: Session, admin_reply_id: int):
    admin_reply = get_admin_reply(db, admin_reply_id)
    admin_reply_repository.delete(db, admin_reply)