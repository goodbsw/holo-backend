from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.models import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False)  # 'customer' or 'attorney'
    subscription_type = Column(String(20), nullable=True)  # 'per_doc', 'subscription'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    plaintiff_cases = relationship("Case", back_populates="plaintiff", foreign_keys="Case.plaintiff_id")
    defendant_cases = relationship("Case", back_populates="defendant", foreign_keys="Case.defendant_id")
    assigned_cases = relationship("Case", back_populates="assigned_attorney", foreign_keys="Case.assigned_attorney_id")
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
    attorney_verification = relationship("AttorneyVerification", back_populates="user", uselist=False) 