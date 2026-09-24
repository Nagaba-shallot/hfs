from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Admin_reply(Base):
    __tablename__ = "admin_reply"

    admin_reply_id = Column(Integer, primary_key=True, index=True)
    feedback_response_id = Column(
        Integer,
        ForeignKey("feedback_response.feedback_response_id"),
        nullable=False,
    )
    admin_id = Column(Integer, ForeignKey("admin.admin_id"), nullable=False)
    reply_text = Column(Text, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feedback_response = relationship("Feedback_response", back_populates="admin_reply")
    
    admin = relationship("Admin")