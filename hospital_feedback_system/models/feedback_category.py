from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Feedback_category(Base):
    __tablename__ = "feedback_category"

    feedback_category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    display_order = Column(Integer, nullable=False)             
    icon = Column(String, default=None, nullable=True)
    description = Column(Text, nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("Questions", back_populates="Feedback_category")