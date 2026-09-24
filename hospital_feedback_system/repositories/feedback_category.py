from hospital_feedback_system.models.feedback_category import Feedback_category
from sqlalchemy.orm import Session

class FeedbackCategoryRepository:
    def __init__(self):
        self.model = Feedback_category

    def get(self, db:Session, department_id:int):
        return db.get(Feedback_category, department_id)

    def get_all(self, db:Session):
        return db.query(Feedback_category).all()

    def create(self, db:Session, data:dict):
        feedback_category=Feedback_category(**data)
        db.add(feedback_category)
        db.commit()
        db.refresh(feedback_category)
        return feedback_category

    def update(self, db:Session, db_obj:Feedback_category, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Feedback_category):
        db.delete(db_obj)
        db.commit()

feedback_category_repository=FeedbackCategoryRepository()