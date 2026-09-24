from hospital_feedback_system.models.survey_progress import Survey_progress
from sqlalchemy.orm import Session

class SurveyProgressRepository:
    def __init__(self):
        self.model = Survey_progress

    def get(self, db:Session, admin_id:int):
        return db.get(Survey_progress, admin_id)

    def get_all(self, db:Session):
        return db.query(Survey_progress).all()

    def create(self, db:Session, data:dict):
        survey_progress=Survey_progress(**data)
        db.add(survey_progress)
        db.commit()
        db.refresh(survey_progress)
        return survey_progress

    def update(self, db:Session, db_obj:Survey_progress, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Survey_progress):
        db.delete(db_obj)
        db.commit()

survey_progress_repository=SurveyProgressRepository()