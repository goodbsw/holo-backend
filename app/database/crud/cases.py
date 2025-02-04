from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict
from datetime import datetime

def get_case(db: Session, case_id: int) -> Optional[Dict]:
    query = text("""
        SELECT c.*, 
               p.name as plaintiff_name,
               d.name as defendant_name,
               a.name as attorney_name
        FROM cases c
        LEFT JOIN users p ON c.plaintiff_id = p.id
        LEFT JOIN users d ON c.defendant_id = d.id
        LEFT JOIN users a ON c.assigned_attorney_id = a.id
        WHERE c.id = :case_id
    """)
    result = db.execute(query, {"case_id": case_id}).first()
    return dict(result) if result else None

def get_user_cases(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict]:
    query = text("""
        SELECT c.*, 
               p.name as plaintiff_name,
               d.name as defendant_name,
               a.name as attorney_name
        FROM cases c
        LEFT JOIN users p ON c.plaintiff_id = p.id
        LEFT JOIN users d ON c.defendant_id = d.id
        LEFT JOIN users a ON c.assigned_attorney_id = a.id
        WHERE c.plaintiff_id = :user_id
        ORDER BY c.created_at DESC
        OFFSET :skip
        LIMIT :limit
    """)
    results = db.execute(
        query, 
        {"user_id": user_id, "skip": skip, "limit": limit}
    ).fetchall()
    return [dict(row) for row in results]

def get_attorney_cases(db: Session, attorney_id: int, skip: int = 0, limit: int = 100) -> List[Dict]:
    query = text("""
        SELECT c.*, 
               p.name as plaintiff_name,
               d.name as defendant_name,
               a.name as attorney_name
        FROM cases c
        LEFT JOIN users p ON c.plaintiff_id = p.id
        LEFT JOIN users d ON c.defendant_id = d.id
        LEFT JOIN users a ON c.assigned_attorney_id = a.id
        WHERE c.assigned_attorney_id = :attorney_id
        ORDER BY c.created_at DESC
        OFFSET :skip
        LIMIT :limit
    """)
    results = db.execute(
        query, 
        {"attorney_id": attorney_id, "skip": skip, "limit": limit}
    ).fetchall()
    return [dict(row) for row in results]

def create_case(db: Session, case_data: dict) -> Dict:
    query = text("""
        INSERT INTO cases (
            case_type, plaintiff_id, defendant_id, assigned_attorney_id,
            status, created_at, updated_at
        ) VALUES (
            :case_type, :plaintiff_id, :defendant_id, :assigned_attorney_id,
            :status, :created_at, :updated_at
        ) RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "case_type": case_data["case_type"],
            "plaintiff_id": case_data["plaintiff_id"],
            "defendant_id": case_data.get("defendant_id"),
            "assigned_attorney_id": case_data.get("assigned_attorney_id"),
            "status": case_data.get("status", "in_progress"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result)

def update_case(db: Session, case_id: int, case_data: dict) -> Optional[Dict]:
    # 동적으로 업데이트할 필드 생성
    update_fields = []
    params = {"case_id": case_id, "updated_at": datetime.now()}
    
    for key, value in case_data.items():
        if key in ["case_type", "defendant_id", "assigned_attorney_id", "status"]:
            update_fields.append(f"{key} = :{key}")
            params[key] = value
    
    if not update_fields:
        return None
    
    query = text(f"""
        UPDATE cases 
        SET {", ".join(update_fields)},
            updated_at = :updated_at
        WHERE id = :case_id
        RETURNING *
    """)
    
    result = db.execute(query, params).first()
    db.commit()
    return dict(result) if result else None

def delete_case(db: Session, case_id: int) -> bool:
    query = text("""
        DELETE FROM cases
        WHERE id = :case_id
        RETURNING id
    """)
    
    result = db.execute(query, {"case_id": case_id}).first()
    db.commit()
    return bool(result)

def assign_attorney(db: Session, case_id: int, attorney_id: int) -> Optional[Dict]:
    query = text("""
        UPDATE cases
        SET assigned_attorney_id = :attorney_id,
            status = 'assigned',
            updated_at = :updated_at
        WHERE id = :case_id
        RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "case_id": case_id,
            "attorney_id": attorney_id,
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result) if result else None 