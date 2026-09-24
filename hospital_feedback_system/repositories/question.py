from hospital_feedback_system.models.question import Questions
from sqlalchemy.orm import Session

class QuestionsRepository:
    def __init__(self):
        self.model = Questions

    def get(self, db:Session, admin_id:int):
        return db.get(Questions, admin_id)

    def get_all(self, db:Session):
        return db.query(Questions).all()

    def create(self, db:Session, data:dict):
        questions=Questions(**data)
        db.add(questions)
        db.commit()
        db.refresh(questions)
        return questions

    def update(self, db:Session, db_obj:Questions, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Questions):
        db.delete(db_obj)
        db.commit()

questions_repository=QuestionsRepository()