from typing import Dict, Optional
import requests

class OAuthHandler:
    @staticmethod
    async def verify_kakao_token(access_token: str) -> Optional[Dict]:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://kauth.kakao.com/oauth/authorize", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

    @staticmethod
    async def verify_naver_token(access_token: str) -> Optional[Dict]:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

    @staticmethod
    async def verify_google_token(access_token: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None 