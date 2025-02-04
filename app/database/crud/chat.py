from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict
from datetime import datetime

def create_chat_message(db: Session, session_id: int, role: str, content: str) -> Dict:
    query = text("""
        INSERT INTO chat_messages (
            session_id, role, content, created_at
        ) VALUES (
            :session_id, :role, :content, :created_at
        ) RETURNING *
    """)

    result = db.execute(
        query,
        {
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result._mapping) if result else None

def get_chat_history(db: Session, session_id: int) -> List[Dict]:
    query = text("""
        SELECT 
            id,
            session_id,
            role,
            content,
            created_at
        FROM chat_messages
        WHERE session_id = :session_id
        ORDER BY created_at ASC
    """)
    
    results = db.execute(query, {"session_id": session_id}).fetchall()
    return [dict(row._mapping) for row in results]

def update_session_context(db: Session, session_id: int, context_data: dict) -> Dict:
    query = text("""
        UPDATE chat_sessions
        SET context_data = :context_data,
            updated_at = :updated_at
        WHERE id = :session_id
        RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "session_id": session_id,
            "context_data": context_data,
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result)