from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.auth import OAuthAccount, AttorneyVerification
from app.models.users import User
from typing import Optional, List, Dict
from datetime import datetime

# OAuth Account CRUD
def get_oauth_account(db: Session, provider: str, provider_account_id: str) -> Optional[Dict]:
    query = text("""
        SELECT * FROM oauth_accounts 
        WHERE provider = :provider 
        AND provider_account_id = :provider_account_id
    """)
    result = db.execute(
        query, 
        {"provider": provider, "provider_account_id": provider_account_id}
    ).first()
    return dict(result) if result else None

def create_oauth_account(db: Session, user_id: int, oauth_data: dict) -> Dict:
    query = text("""
        INSERT INTO oauth_accounts (
            user_id, provider, provider_account_id, provider_data,
            created_at, updated_at
        ) VALUES (
            :user_id, :provider, :provider_account_id, :provider_data,
            :created_at, :updated_at
        ) RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "user_id": user_id,
            "provider": oauth_data["provider"],
            "provider_account_id": oauth_data["provider_account_id"],
            "provider_data": oauth_data.get("provider_data", {}),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result)

def update_oauth_account(db: Session, oauth_id: int, oauth_data: dict) -> Optional[Dict]:
    query = text("""
        UPDATE oauth_accounts 
        SET provider_data = :provider_data,
            updated_at = :updated_at
        WHERE id = :oauth_id
        RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "provider_data": oauth_data.get("provider_data", {}),
            "updated_at": datetime.now(),
            "oauth_id": oauth_id
        }
    ).first()
    
    db.commit()
    return dict(result) if result else None

# Attorney Verification CRUD
def get_attorney_verification(db: Session, user_id: int) -> Optional[Dict]:
    query = text("""
        SELECT * FROM attorney_verifications
        WHERE user_id = :user_id
    """)
    result = db.execute(query, {"user_id": user_id}).first()
    return dict(result) if result else None

def get_attorney_by_license(db: Session, license_number: str) -> Optional[Dict]:
    query = text("""
        SELECT * FROM attorney_verifications
        WHERE license_number = :license_number
    """)
    result = db.execute(query, {"license_number": license_number}).first()
    return dict(result) if result else None

def create_attorney_verification(db: Session, verification_data: dict) -> Dict:
    query = text("""
        INSERT INTO attorney_verifications (
            user_id, license_number, bar_association, law_firm,
            verification_status, document_urls, created_at, updated_at
        ) VALUES (
            :user_id, :license_number, :bar_association, :law_firm,
            :verification_status, :document_urls, :created_at, :updated_at
        ) RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "user_id": verification_data["user_id"],
            "license_number": verification_data["license_number"],
            "bar_association": verification_data["bar_association"],
            "law_firm": verification_data.get("law_firm"),
            "verification_status": "pending",
            "document_urls": verification_data.get("document_urls", {}),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ).first()
    
    db.commit()
    return dict(result)

def update_verification_status(
    db: Session, 
    user_id: int, 
    status: str, 
    rejection_reason: Optional[str] = None
) -> Optional[Dict]:
    query = text("""
        UPDATE attorney_verifications
        SET verification_status = :status,
            verification_date = :verification_date,
            rejection_reason = :rejection_reason,
            updated_at = :updated_at
        WHERE user_id = :user_id
        RETURNING *
    """)
    
    result = db.execute(
        query,
        {
            "status": status,
            "verification_date": datetime.now(),
            "rejection_reason": rejection_reason,
            "updated_at": datetime.now(),
            "user_id": user_id
        }
    ).first()
    
    db.commit()
    return dict(result) if result else None

def get_pending_verifications(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    query = text("""
        SELECT * FROM attorney_verifications
        WHERE verification_status = 'pending'
        ORDER BY created_at DESC
        OFFSET :skip
        LIMIT :limit
    """)
    
    results = db.execute(query, {"skip": skip, "limit": limit}).fetchall()
    return [dict(row) for row in results] 