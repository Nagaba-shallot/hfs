from hospital_feedback_system.models.admin import Admin
from sqlalchemy.orm import Session

class AdminRepository:
    def __init__(self):
        self.model = Admin

    def get(self, db:Session, admin_id:int):
        return db.get(Admin, admin_id)

    def get_all(self, db:Session):
        return db.query(Admin).all()

    def create(self, db:Session, data:dict):
        admin=Admin(**data)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    def update(self, db:Session, db_obj:Admin, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Admin):
        db.delete(db_obj)
        db.commit()

admin_repository=AdminRepository()