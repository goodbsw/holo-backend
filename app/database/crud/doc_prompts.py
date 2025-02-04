from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict
from datetime import datetime

def get_doc_prompt(db: Session, case_type: str, doc_type: str) -> Optional[Dict]:
    query = text("""
        SELECT * FROM doc_prompts 
        WHERE case_type = :case_type 
        AND doc_type = :doc_type
    """)
    result = db.execute(
        query, 
        {"case_type": case_type, "doc_type": doc_type}
    ).first()
    return dict(result._mapping) if result else None

def get_doc_prompts(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    query = text("""
        SELECT * FROM doc_prompts
        ORDER BY case_type, doc_type
        OFFSET :skip
        LIMIT :limit
    """)
    results = db.execute(query, {"skip": skip, "limit": limit}).fetchall()
    return [dict(row) for row in results]

def create_doc_prompt(db: Session, prompt_data: dict) -> Dict:
    query = text("""
        INSERT INTO doc_prompts (
            case_type, doc_type, prompt_text
        ) VALUES (
            :case_type, :doc_type, :prompt_text
        ) RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "case_type": prompt_data["case_type"],
            "doc_type": prompt_data["doc_type"],
            "prompt_text": prompt_data["prompt_text"]
        }
    ).first()
    
    db.commit()
    return dict(result)

def update_doc_prompt(db: Session, prompt_id: int, prompt_data: dict) -> Optional[Dict]:
    query = text("""
        UPDATE doc_prompts 
        SET case_type = :case_type,
            doc_type = :doc_type,
            prompt_text = :prompt_text
        WHERE id = :prompt_id
        RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "prompt_id": prompt_id,
            "case_type": prompt_data["case_type"],
            "doc_type": prompt_data["doc_type"],
            "prompt_text": prompt_data["prompt_text"]
        }
    ).first()
    
    db.commit()
    return dict(result) if result else None

def delete_doc_prompt(db: Session, prompt_id: int) -> bool:
    query = text("""
        DELETE FROM doc_prompts
        WHERE id = :prompt_id
        RETURNING id
    """)
    
    result = db.execute(query, {"prompt_id": prompt_id}).first()
    db.commit()
    return bool(result) 