from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict
from app.models.documents import Draft
from datetime import datetime

def create_draft(db: Session, session_id: str, doc_type: str, draft: str) -> Draft:
    query = text("""
        INSERT INTO drafts (session_id, title, content, updated_at)
        VALUES (:session_id, :title, :content, :updated_at) RETURNING *
    """)
    result =db.execute(query,
               {"session_id": session_id,
                "title": doc_type,
                "content": draft,
                "updated_at": datetime.now()}).first()
    db.commit()
    return dict(result._mapping) if result else None

def update_draft(db: Session, session_id: str, content: str) -> Dict:
    query = text("""
        UPDATE drafts
        SET content = :content,
            updated_at = :updated_at
        WHERE session_id = :session_id
        RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "session_id": session_id,
            "content": content,
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result._mapping) if result else None

def get_draft(db: Session, session_id: str) -> Optional[Draft]:
    query = text("""
        SELECT * FROM drafts WHERE session_id = :session_id
    """)
    result = db.execute(query, {"session_id": session_id}).first()
    return dict(result._mapping) if result else None