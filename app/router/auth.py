from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.crud import auth as crud_auth
from app.utils.oauth import OAuthHandler
from typing import Dict

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/oauth/{provider}")
async def oauth_login(
    provider: str,
    db: Session = Depends(get_db)
):
    """
    OAuth 로그인 처리 (카카오/네이버/구글)
    """
    oauth_handler = OAuthHandler()
    
    # Verify token with provider
    if provider == "kakao":
        user_info = await oauth_handler.verify_kakao_token()
    elif provider == "naver":
        user_info = await oauth_handler.verify_naver_token()
    elif provider == "google":
        user_info = await oauth_handler.verify_google_token()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    # Check if OAuth account exists
    oauth_account = crud_auth.get_oauth_account(
        db, 
        provider=provider,
        provider_account_id=str(user_info.get("id"))
    )
    
    if not oauth_account:
        # Create new user and OAuth account
        # Implementation depends on your user creation logic
        pass
    
    # Generate JWT token and return
    return {"access_token": "your-jwt-token"}

@router.post("/attorney/verify")
async def verify_attorney(
    verification_data: Dict,
    db: Session = Depends(get_db)
):
    """
    변호사 자격 검증 신청
    """
    # Check if license number already exists
    existing_verification = crud_auth.get_attorney_by_license(
        db, 
        verification_data["license_number"]
    )
    
    if existing_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already registered"
        )
    
    return crud_auth.create_attorney_verification(db, verification_data)

@router.put("/attorney/verify/{user_id}")
async def update_attorney_status(
    user_id: int,
    status: str,
    rejection_reason: str = None,
    db: Session = Depends(get_db)
):
    """
    변호사 자격 검증 상태 업데이트 (관리자용)
    """
    verification = crud_auth.update_verification_status(
        db, 
        user_id, 
        status, 
        rejection_reason
    )
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification request not found"
        )
    
    return verification 