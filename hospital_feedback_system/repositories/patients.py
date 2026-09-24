from hospital_feedback_system.models.patients import Patients
from sqlalchemy.orm import Session

class PatientsRepository:
    def __init__(self):
        self.model = Patients

    def get(self, db:Session, admin_id:int):
        return db.get(Patients, admin_id)

    def get_all(self, db:Session):
        return db.query(Patients).all()

    def create(self, db:Session, data:dict):
        patients=Patients(**data)
        db.add(patients)
        db.commit()
        db.refresh(patients)
        return patients

    def update(self, db:Session, db_obj:Patients, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Patients):
        db.delete(db_obj)
        db.commit()

patients_repository=PatientsRepository()