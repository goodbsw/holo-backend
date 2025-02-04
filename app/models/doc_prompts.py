from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class DocPrompt(Base):
    __tablename__ = "doc_prompts"

    id = Column(Integer, primary_key=True, index=True)
    case_type = Column(String(50), nullable=False)  # '민사-임대차', '형사-사기' 등
    doc_type = Column(String(50), nullable=False)   # '소장', '항소장', '준비서면' 등
    prompt_text = Column(Text, nullable=False)      # ChatGPT system role / template prompt 