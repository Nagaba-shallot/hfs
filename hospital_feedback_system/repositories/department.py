from hospital_feedback_system.models.department import Department
from sqlalchemy.orm import Session

class DepartmentRepository:
    def __init__(self):
        self.model = Department

    def get(self, db:Session, department_id:int):
        return db.get(Department, department_id)

    def get_all(self, db:Session):
        return db.query(Department).all()

    def create(self, db:Session, data:dict):
        department=Department(**data)
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    def update(self, db:Session, db_obj:Department, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Department):
        db.delete(db_obj)
        db.commit()

department_repository=DepartmentRepository()