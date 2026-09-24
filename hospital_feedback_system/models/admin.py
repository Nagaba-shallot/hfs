from datetime import datetime
from hospital_feedback_system.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    hospital_name = Column(String, nullable=False)
    role = Column(String, default="admin", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    admin_reply = relationship("Admin_reply", back_populates="Admin")