from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(20), nullable=False)  # 'kakao', 'naver', 'google'
    provider_account_id = Column(String(100), nullable=False)
    provider_data = Column(JSON)  # Store additional OAuth data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="oauth_accounts")

class AttorneyVerification(Base):
    __tablename__ = "attorney_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)  # 변호사 등록 번호
    bar_association = Column(String(50), nullable=False)  # 소속 지방변호사회
    law_firm = Column(String(100))  # 소속 법무법인
    verification_status = Column(String(20), default="pending")  # pending, approved, rejected
    verification_date = Column(DateTime)  # 승인/거절 날짜
    document_urls = Column(JSON)  # 자격증, 신분증 등 증빙서류 URL
    rejection_reason = Column(String(500))  # 거절 시 사유
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="attorney_verification") 