from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict
import os

# AI Refine (기존 코드 유지를 가정)
from openai import OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

from docxtpl import DocxTemplate  # 서버단에서 DOCX 치환용

router = APIRouter()

DOCUMENTS_DIR = "/Users/seungweonbaek/Downloads"

# ------------------------------
# 1) 템플릿 원본 문서 다운로드
# ------------------------------
@router.get("/documents/{filename}")
async def get_document(filename: str):
    """
    DOCUMENTS_DIR 아래 있는 DOCX 문서를 직접 다운로드 (원본 템플릿 등)
    """
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)

# ------------------------------
# 2) AI 문맥 다듬기 API (기존)
# ------------------------------
class DocumentRefineRequest(BaseModel):
    document_id: str
    field_name: str
    user_input: str

@router.post("/documents/refine")
async def refine_document(request: DocumentRefineRequest):
    """
    사용자가 입력한 문서 필수 항목을 ChatGPT를 이용하여 문맥을 다듬어 반환
    """
    try:
        prompt = f"""
        다음 문서 필수 항목을 법리적으로 더 적합한 문맥으로 다듬어 주세요.
        
        문서 ID: {request.document_id}
        필드명: {request.field_name}
        사용자 입력: {request.user_input}
        
        법률 문서 스타일을 유지하면서 보다 정확하고 전문적인 문맥으로 변환해 주세요.
        - 문서 ID, 필드명, 사용자 입력이라는 키워드는 포함하지 않아야합니다.
        - 필드명과 사용자 입력의 내용이 포함되어야 합니다.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 예시 모델명
            messages=[
                {"role": "system", "content": "당신은 비법조인의 법적 문서 작성을 도와주는 법률 전문가입니다."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        refined_text = response.choices[0].message.content.strip()
        return {"refined_text": refined_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChatGPT 요청 실패: {str(e)}")


# ------------------------------
# 3) 최종 문서 생성 API
# ------------------------------
class DocumentGenerateRequest(BaseModel):
    template_filename: str
    user_inputs: Dict[str, str]

@router.post("/documents/generate")
async def generate_document(req: DocumentGenerateRequest):
    """
    1) DOCUMENTS_DIR 아래에 있는 템플릿 DOCX 파일을 불러옴
    2) docxtpl 로 placeholders 치환
    3) 치환된 문서를 임시 파일로 저장 후, 해당 파일을 FileResponse 로 반환
    """
    template_path = os.path.join(DOCUMENTS_DIR, req.template_filename)
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="DOCX 템플릿을 찾을 수 없습니다.")

    try:
        doc = DocxTemplate(template_path)
        doc.render(req.user_inputs)
        output_filename = f"generated_{req.template_filename}"
        output_path = os.path.join(DOCUMENTS_DIR, output_filename)
        doc.save(output_path)

        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX 템플릿 치환 실패: {str(e)}")
