from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.database.crud import doc_prompts as crud_prompts
from app.database.crud import chat as crud_chat
from app.database.crud import documents as crud_documents
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.config import get_settings
from openai import OpenAI
import markdown
import difflib

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

router = APIRouter(prefix="/documents", tags=["documents"])

class GenerateDraftRequest(BaseModel):
    session_id: str
    case_type: str
    doc_type: str

@router.post("/generate_draft")
async def generate_draft(request: GenerateDraftRequest, db: Session = Depends(get_db)):
    """
    사용자가 입력한 문서 필수 항목을 ChatGPT를 이용하여 문맥을 다듬어 반환
    """
    session_id = request.session_id
    case_type = request.case_type
    doc_type = request.doc_type

    doc_prompt = crud_prompts.get_doc_prompt(db, case_type, doc_type)
    if not doc_prompt:
        raise HTTPException(status_code=404, detail="문서 유형을 찾을 수 없습니다.")
    
    messages = [{"role": "system", "content": doc_prompt["prompt_text"]}]

    chat_history = crud_chat.get_chat_history(db, session_id)
    for message in chat_history:
        messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )

    draft = markdown.markdown(response.choices[0].message.content)
    crud_documents.create_draft(db, session_id, doc_type, draft)

    return {"session_id": session_id, "draft": draft}

class UpdateDraftRequest(BaseModel):
    session_id: str

def get_text_changes(old_text: str, new_text: str) -> dict:
    """텍스트 간의 차이점을 찾아 반환"""
    differ = difflib.SequenceMatcher(None, old_text, new_text)
    changes = []
    
    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag != 'equal':  # 변경된 부분만 추출
            changes.append({
                'type': tag,  # 'replace', 'delete', 'insert' 중 하나
                'oldText': old_text[i1:i2],
                'newText': new_text[j1:j2],
                'position': {'start': i1, 'end': i2}
            })
    
    return {'changes': changes}

@router.post("/update_draft")
async def update_draft(request: UpdateDraftRequest, db: Session = Depends(get_db)):
    """
    사용자가 입력한 문서 필수 항목을 ChatGPT를 이용하여 문맥을 다듬어 반환
    """
    draft = crud_documents.get_draft(db, request.session_id)
    if not draft:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    
    old_content = draft["content"]
    session_id = request.session_id
    
    messages = [
        {"role": "system", "content": '''
            1. 사용자의 수정 요청을 반영하여 초안을 수정하여 반환해주세요.
            2. 수정 요청 외에는 초안을 그대로 반환해주세요.
        '''},
        {"role": "user", "content": f"Draft content: {old_content}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )

    updated_draft = markdown.markdown(response.choices[0].message.content)
    crud_documents.update_draft(db, request.session_id, updated_draft)
    
    # 변경사항 찾기
    changes = get_text_changes(old_content, updated_draft)

    return {
        "session_id": session_id,
        "updated_draft": updated_draft,
        "changes": changes,
        "message": "요청하신 내용을 반영하여 수정하였습니다."
    }