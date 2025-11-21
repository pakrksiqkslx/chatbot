from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import uvicorn
import logging
from config import settings
from direct_pinecone_service import get_vectorstore_service
from hyperclova_client import get_hyperclova_client
from database import db_instance
from routers import auth

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
    root_path=settings.ROOT_PATH,
    openapi_url=(f"{settings.API_PREFIX}{settings.OPENAPI_URL}" if settings.ENABLE_DOCS else None),
    docs_url=(f"{settings.API_PREFIX}{settings.DOCS_URL}" if settings.ENABLE_DOCS else None),
    redoc_url=(f"{settings.API_PREFIX}{settings.REDOC_URL}" if settings.ENABLE_DOCS else None),
)

# 보안 미들웨어 설정
if settings.ENVIRONMENT == "production":
    # 기본 허용 호스트(프로덕션 도메인)
    allowed_hosts = ["*.bu-chatbot.co.kr"]

    # 내부 테스트/헬스체크 용도로 로컬호스트를 허용하려면
    # 환경변수 ALLOW_LOCALHOST_IN_PROD=true 로 켜십시오.
    import os
    if os.getenv("ALLOW_LOCALHOST_IN_PROD", "false").lower() in ("1", "true", "yes"):
        allowed_hosts += ["localhost", "127.0.0.1"]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )

# CORS middleware 설정
if settings.ALLOWED_ORIGINS == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

router = APIRouter(prefix=settings.API_PREFIX)

# Validation Error 핸들러 추가 (422 에러 로깅)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """422 Validation Error를 상세히 로깅"""
    errors = exc.errors()
    error_details = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        error_details.append({
            "field": field,
            "message": error.get("msg"),
            "type": error.get("type")
        })
    
    logger.warning(
        f"Validation Error - {request.method} {request.url.path}: {error_details}"
    )
    
    # 기본 FastAPI validation error 응답 반환
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

# 라우터 등록
app.include_router(auth.router, prefix=settings.API_PREFIX)

# MongoDB 연결 이벤트
@app.on_event("startup")
async def startup_db_client():
    """앱 시작 시 MongoDB 연결"""
    await db_instance.connect_db()
    logger.info("MongoDB Atlas 연결 완료")


@router.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트 - 실제 의존성 연결 상태 확인"""
    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Pinecone 연결 상태 확인
    pinecone_status = "unknown"
    try:
        vectorstore = get_vectorstore_service()
        if vectorstore and vectorstore.index:
            # 간단한 연결 테스트 (인덱스 정보 확인)
            # 실제 쿼리는 하지 않고 클라이언트만 확인
            pinecone_status = "healthy"
            health_status["checks"]["pinecone"] = {
                "status": "healthy",
                "index_name": settings.PINECONE_INDEX_NAME
            }
        else:
            pinecone_status = "unhealthy"
            health_status["checks"]["pinecone"] = {
                "status": "unhealthy",
                "error": "Pinecone index not initialized"
            }
    except Exception as e:
        pinecone_status = "unhealthy"
        health_status["checks"]["pinecone"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        logger.warning(f"Pinecone health check failed: {e}")
    
    hyperclova_status = "unknown"
    try:
        if settings.HYPERCLOVA_API_KEY:
            hyperclova_status = "healthy"
            health_status["checks"]["hyperclova"] = {
                "status": "healthy",
                "api_key_configured": True
            }
        else:
            hyperclova_status = "unhealthy"
            health_status["checks"]["hyperclova"] = {
                "status": "unhealthy",
                "error": "HyperCLOVA API key not configured"
            }
    except Exception as e:
        hyperclova_status = "unhealthy"
        health_status["checks"]["hyperclova"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        logger.warning(f"HyperCLOVA health check failed: {e}")
    
    # 전체 상태 결정 (하나라도 unhealthy면 unhealthy)
    if pinecone_status == "unhealthy" or hyperclova_status == "unhealthy":
        health_status["status"] = "unhealthy"
        # HTTP 503 반환 (로드 밸런서가 헬스 체크 실패로 인식)
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status

@router.get("/metrics")
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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    수업계획서 기반 챗봇 엔드포인트
    
    1. 질문 의도 분류 (수업 관련 vs 일상 대화)
    2. 수업 관련: PINECONE 검색 + HyperCLOVA 직접 답변
    3. 일상 대화: HyperCLOVA 직접 답변
    """
    try:
        logger.info(f"채팅 요청: {request.query}")
        
        # HyperCLOVA 클라이언트 초기화
        hyperclova = get_hyperclova_client()
        
        # 1. 질문 의도 분류 (비동기)
        intent = await hyperclova.classify_intent(request.query)
        logger.info(f"질문 의도: {intent}")
        
        # 2. 일상 대화인 경우 바로 답변 (비동기)
        if intent == 'casual_chat':
            logger.info("일상 대화로 분류 - 직접 답변 생성")
            answer = await hyperclova.generate_casual_answer(request.query)
            
            return ChatResponse(
                answer=answer,
                sources=[]
            )
        
        # 3. PINECONE 벡터 검색 (비동기)
        logger.info(f"{intent} 분류 - 벡터 검색 수행")
        
        vectorstore = get_vectorstore_service()
        search_results = await vectorstore.similarity_search(
            query=request.query,
            k=request.k
        )
        
        if not search_results:
            return ChatResponse(
                answer="죄송합니다. 관련 수업 정보를 찾을 수 없습니다. 다른 방식으로 질문해주시겠어요?",
                sources=[]
            )
        
        logger.info(f"검색된 문서 수: {len(search_results)}")
        
        # 4. HyperCLOVA가 직접 질문을 이해하고 답변 생성 (비동기)
        answer = await hyperclova.generate_answer(
            query=request.query,
            context_docs=search_results
        )
        
        # 응답 구성
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
        raise HTTPException(
            status_code=500, 
            detail="서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )

app.include_router(router)

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
