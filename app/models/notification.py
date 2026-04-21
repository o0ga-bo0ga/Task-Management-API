from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    created_at = Column(DateTime, index=True, server_default=func.now())
    is_read = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")

     