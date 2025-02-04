from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict
from datetime import datetime

def get_user(db: Session, user_id: int) -> Optional[Dict]:
    query = text("""
        SELECT * FROM users 
        WHERE id = :user_id
    """)
    result = db.execute(query, {"user_id": user_id}).first()
    return dict(result) if result else None

def get_user_by_email(db: Session, email: str) -> Optional[Dict]:
    query = text("""
        SELECT * FROM users 
        WHERE email = :email
    """)
    result = db.execute(query, {"email": email}).first()
    return dict(result) if result else None

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    query = text("""
        SELECT * FROM users
        ORDER BY created_at DESC
        OFFSET :skip
        LIMIT :limit
    """)
    results = db.execute(query, {"skip": skip, "limit": limit}).fetchall()
    return [dict(row) for row in results]

def create_user(db: Session, user_data: dict) -> Dict:
    query = text("""
        INSERT INTO users (
            email, password, name, user_type, subscription_type,
            created_at, updated_at
        ) VALUES (
            :email, :password, :name, :user_type, :subscription_type,
            :created_at, :updated_at
        ) RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "email": user_data["email"],
            "password": user_data["password"],
            "name": user_data["name"],
            "user_type": user_data["user_type"],
            "subscription_type": user_data.get("subscription_type"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result)

def update_user(db: Session, user_id: int, user_data: dict) -> Optional[Dict]:
    # 동적으로 업데이트할 필드 생성
    update_fields = []
    params = {"user_id": user_id, "updated_at": datetime.now()}
    
    for key, value in user_data.items():
        if key in ["email", "password", "name", "user_type", "subscription_type"]:
            update_fields.append(f"{key} = :{key}")
            params[key] = value
    
    if not update_fields:
        return None
    
    query = text(f"""
        UPDATE users 
        SET {", ".join(update_fields)},
            updated_at = :updated_at
        WHERE id = :user_id
        RETURNING *
    """)
    
    result = db.execute(query, params).first()
    db.commit()
    return dict(result) if result else None

def delete_user(db: Session, user_id: int) -> bool:
    query = text("""
        DELETE FROM users
        WHERE id = :user_id
        RETURNING id
    """)
    
    result = db.execute(query, {"user_id": user_id}).first()
    db.commit()
    return bool(result) 