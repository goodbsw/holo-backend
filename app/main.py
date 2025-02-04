from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import documents, chat

app = FastAPI(title="AI Legal Document API")

# 허용할 오리진을 설정합니다.
origins = [
    "http://localhost:3001",
    # 필요에 따라 다른 오리진 추가 가능
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 프론트엔드 도메인을 명시적으로 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(documents.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "AI Legal Document API is running!"}
