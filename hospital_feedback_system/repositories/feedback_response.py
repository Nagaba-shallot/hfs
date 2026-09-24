from hospital_feedback_system.models.feedback_response import Feedback_response
from sqlalchemy.orm import Session

class FeedbackResponseRepository:
    def __init__(self):
        self.model = Feedback_response

    def get(self, db:Session, department_id:int):
        return db.get(Feedback_response, department_id)

    def get_all(self, db:Session):
        return db.query(Feedback_response).all()

    def create(self, db:Session, data:dict):
        feedback_response=Feedback_response(**data)
        db.add(feedback_response)
        db.commit()
        db.refresh(feedback_response)
        return feedback_response

    def update(self, db:Session, db_obj:Feedback_response, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Feedback_response):
        db.delete(db_obj)
        db.commit()

feedback_response_repository=FeedbackResponseRepository()