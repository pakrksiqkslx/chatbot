"""
FastAPI 애플리케이션 진입점
"""
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
import os

from infrastructure.config import settings
from infrastructure.database import db_instance
from domain.chat.vectorstore import get_vectorstore_service
from api import auth, conversations

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

# CORS middleware 설정 (먼저 추가 - 역순 실행이므로 나중에 실행됨)
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

# 보안 미들웨어 설정 (나중에 추가 - 먼저 실행됨)
# TrustedHostMiddleware는 개발 환경에서는 비활성화 (OPTIONS 요청 문제 방지)
# 프로덕션에서는 환경변수로 제어 (기본값: 비활성화 - ECS/nginx 프록시 환경에서는 호스트 검증 불필요)
if settings.ENVIRONMENT == "production" and os.getenv("ENABLE_TRUSTED_HOST", "false").lower() in ("1", "true", "yes"):
    allowed_hosts = ["*.bu-chatbot.co.kr", "bu-chatbot.co.kr"]
    
    # 내부 테스트/헬스체크 용도로 로컬호스트를 허용하려면
    # 환경변수 ALLOW_LOCALHOST_IN_PROD=true 로 켜십시오.
    if os.getenv("ALLOW_LOCALHOST_IN_PROD", "false").lower() in ("1", "true", "yes"):
        allowed_hosts += ["localhost", "127.0.0.1"]
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

router = APIRouter(prefix=settings.API_PREFIX)

# 400 Bad Request 핸들러 추가
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 예외 핸들러 - 400 에러 등 상세 로깅"""
    logger.warning(
        f"HTTP {exc.status_code} Error - {request.method} {request.url.path} | "
        f"Host: {request.headers.get('host', 'unknown')} | "
        f"Origin: {request.headers.get('origin', 'none')} | "
        f"Detail: {exc.detail}"
    )
    
    # 원본 응답 반환
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

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
        f"Validation Error - {request.method} {request.url.path} | "
        f"Host: {request.headers.get('host', 'unknown')} | "
        f"Origin: {request.headers.get('origin', 'none')} | "
        f"Errors: {error_details}"
    )
    
    # 기본 FastAPI validation error 응답 반환
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

# API 라우터 등록
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(conversations.router, prefix=settings.API_PREFIX)
app.include_router(router)

# MongoDB 연결 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    # 프로덕션 환경 설정 검증
    if settings.ENVIRONMENT == "production":
        validate_production_settings()
    
    # MongoDB 연결
    try:
        await db_instance.connect_db()
        logger.info("MongoDB Atlas 연결 완료")
    except Exception as e:
        logger.error(f"MongoDB 연결 실패: {e}")
        if settings.ENVIRONMENT == "production":
            raise
        else:
            logger.warning("개발 환경: MongoDB 연결 실패했지만 앱은 계속 실행됩니다.")


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

def validate_production_settings():
    """프로덕션 환경에서 필수 설정 검증"""
    if settings.ENVIRONMENT == "production":
        required_vars = [
            ("MONGODB_URI", settings.MONGODB_URI),
            ("JWT_SECRET_KEY", settings.JWT_SECRET_KEY),
            ("HYPERCLOVA_API_KEY", settings.HYPERCLOVA_API_KEY),
            ("PINECONE_API_KEY", settings.PINECONE_API_KEY),
            ("SMTP_USER", settings.SMTP_USER),
            ("SMTP_PASSWORD", settings.SMTP_PASSWORD),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value or var_value in ["", "dev-jwt-secret-key-change-me", "your-secret-key-change-this-in-production"]:
                missing_vars.append(var_name)
        
        if missing_vars:
            error_msg = f"프로덕션 환경에서 필수 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # JWT_SECRET_KEY가 기본값인지 확인
        if settings.JWT_SECRET_KEY == "dev-jwt-secret-key-change-me":
            logger.warning("JWT_SECRET_KEY가 기본값입니다. 프로덕션에서는 반드시 변경해야 합니다.")

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # 프로덕션 환경 설정 검증
    try:
        validate_production_settings()
    except ValueError as e:
        logger.error(f"설정 검증 실패: {e}")
        exit(1)
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if settings.ENVIRONMENT == "production" else 1,
        log_level=settings.LOG_LEVEL.lower()
    )
