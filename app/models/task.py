from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class Status(str, enum.Enum):
    PENDING = "PENDING"
    INPROGRESS = "INPROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(64), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, index=True, server_default=func.now())
    status = Column(Enum(Status, name="task_status_type"), nullable=False, default=Status.PENDING)
    updated_at = Column(DateTime, index=True, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="tasks")

     