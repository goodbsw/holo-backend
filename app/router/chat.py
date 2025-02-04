from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from enum import Enum
import uuid
from datetime import datetime
from openai import OpenAI
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.crud import chat as crud_chat
from app.database.crud import doc_prompts as crud_prompts
from app.core.config import get_settings
import json

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: Dict
    session_id: Optional[str] = None

@router.post("/")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # 1) unpack fields
    session_id = request.session_id
    msg_dict = request.message
    role = msg_dict['role']
    content = msg_dict['content']

    if session_id is None:
        # 세션ID가 없다면 새로 생성
        print("session_id is None")
        session_id = str(uuid.uuid4())

    # 2) DB에서 과거 대화 불러오기
    chat_history = crud_chat.get_chat_history(db, session_id)
    # chat_history = [] if no prior messages

    # 3) 메시지 배열 구성
    messages = []

    if not chat_history:
        # 대화가 없는 세션 => system 메시지 딱 한 번 추가
        system_prompt = """
        당신은 비법조인의 법률 전문가입니다. 아래 사항을 준수하세요.
        1. 사용자가 초안 작성에 도움이 되도록 1가지 대답만 할 수 있는 질문을 하세요.
        2. 사용자가 법률 문서 작성 외의 질문을 하면 관련 질문을 하도록 유도해주세요.
        3. 사용자가 요청한 문서 작성에 필요한 정보를 모두 받았다면 초안 작성 버튼을 누르도록 유도해주세요.
        4. 당신은 절대로 초안 작성 또는 예시 작성을 하지마세요.
        """
        messages.append({"role": "system", "content": system_prompt})

    # 이제 기존 대화 DB에 있는 메시지를 messages 에 추가
    for old_msg in chat_history:
        messages.append({
            "role": old_msg['role'],
            "content": old_msg['content']
        })

    # 4) 이번에 들어온 user 메시지도 DB에 저장
    #    (role='user'인 경우)
    crud_chat.create_chat_message(db, session_id, role, content)

    # 그리고 messages에도 append
    messages.append({"role": role, "content": content})

    # 5) ChatGPT 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    gpt_response = response.choices[0].message.content

    # 6) assistant 메시지를 DB에 저장
    crud_chat.create_chat_message(db, session_id, "assistant", gpt_response)

    return {
        "session_id": session_id,
        "response": gpt_response
    }