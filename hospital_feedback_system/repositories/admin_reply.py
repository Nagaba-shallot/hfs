from hospital_feedback_system.models.admin_reply import Admin_reply
from sqlalchemy.orm import Session

class AdminReplyRepository:
    def __init__(self):
        self.model = Admin_reply

    def get(self, db:Session, admin_reply_id:int):
        return db.get(Admin_reply, admin_reply_id)

    def get_all(self, db:Session):
        return db.query(Admin_reply).all()

    def create(self, db:Session, data:dict):
        admin_reply=Admin_reply(**data)
        db.add(admin_reply)
        db.commit()
        db.refresh(admin_reply)
        return admin_reply

    def update(self, db:Session, db_obj:Admin_reply, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Admin_reply):
        db.delete(db_obj)
        db.commit()

admin_reply_repository=AdminReplyRepository()