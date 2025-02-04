from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean
from datetime import datetime
from app.models import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)