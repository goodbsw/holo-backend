from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import documents

app = FastAPI(title="AI Legal Document API")

# CORS 설정 (프론트엔드와 통신 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(documents.router, tags=["Documents"])

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "AI Legal Document API is running!"}
