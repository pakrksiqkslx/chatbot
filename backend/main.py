from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from config import settings
from direct_pinecone_service import get_vectorstore_service
from hyperclova_client import get_hyperclova_client

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# 보안 미들웨어 설정
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# CORS middleware 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION
    }

@app.get("/metrics")
async def metrics():
    """메트릭 엔드포인트 (프로덕션에서는 Prometheus 등 사용)"""
    if not settings.ENABLE_METRICS:
        return {"message": "Metrics disabled"}
    
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL
    }


# 요청/응답 모델
class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    query: str
    k: int = 3  # 검색할 문서 수
    include_sources: bool = True  # 출처 포함 여부


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    answer: str
    sources: list = []


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    수업계획서 기반 챗봇 엔드포인트
    
    1. FAISS에서 유사 문서 검색
    2. HyperCLOVA X로 답변 생성
    """
    try:
        logger.info(f"채팅 요청: {request.query}")
        
        # 1. PINECONE 벡터 검색
        vectorstore = get_vectorstore_service()
        search_results = vectorstore.similarity_search(
            query=request.query,
            k=request.k
        )
        
        if not search_results:
            return ChatResponse(
                answer="죄송합니다. 관련 정보를 찾을 수 없습니다.",
                sources=[]
            )
        
        logger.info(f"검색된 문서 수: {len(search_results)}")
        
        # 2. HyperCLOVA X로 답변 생성
        hyperclova = get_hyperclova_client()
        answer = hyperclova.generate_answer(
            query=request.query,
            context_docs=search_results
        )
        
        # 3. 응답 구성
        sources = []
        if request.include_sources:
            for result in search_results:
                sources.append({
                    "course_name": result["metadata"].get("course_name", ""),
                    "professor": result["metadata"].get("professor", ""),
                    "section": result["metadata"].get("section", ""),
                    "content_preview": result["page_content"][:200] + "..."
                })
        
        logger.info("답변 생성 완료")
        
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"채팅 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if settings.ENVIRONMENT == "production" else 1,
        log_level=settings.LOG_LEVEL.lower()
    )
