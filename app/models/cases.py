from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_type = Column(String(50), nullable=False)  # '민사-임대차', '민사-손해배상' 등
    plaintiff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    defendant_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_attorney_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="in_progress")  # 'in_progress', 'closed', etc
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    plaintiff = relationship("User", back_populates="plaintiff_cases", foreign_keys=[plaintiff_id])
    defendant = relationship("User", back_populates="defendant_cases", foreign_keys=[defendant_id])
    assigned_attorney = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_attorney_id]) 