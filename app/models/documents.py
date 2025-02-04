from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models import Base

class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False)