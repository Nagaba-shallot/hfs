from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Questions(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feedback_category_id = Column(                                     
        Integer,
        ForeignKey("feedback_category.feedback_category_id"),
        nullable=False,
    )
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False, default="rating")
    order_in_feedback_category = Column(Integer, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    min_rating_label = Column(String, nullable=True)                  
    max_rating_label = Column(String, nullable=True)                   
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    Feedback_category = relationship(
        "Feedback_category", back_populates="questions"
    )