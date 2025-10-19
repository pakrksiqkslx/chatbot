"""
애플리케이션 설정 관리
"""
import os
from typing import Optional


class Settings:
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    APP_NAME: str = "Chatbot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # 서버 설정
    HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT", "5000"))
    WORKERS: int = int(os.getenv("BACKEND_WORKERS", "1"))
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000").split(",")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # 외부 API 설정 - HyperCLOVA X
    HYPERCLOVA_API_KEY: str = os.getenv("HYPERCLOVA_API_KEY", "nv-93ec8a8d596946b2b2314d70dcdba676qLCw")
    HYPERCLOVA_API_GATEWAY_KEY: Optional[str] = os.getenv("HYPERCLOVA_API_GATEWAY_KEY")
    HYPERCLOVA_REQUEST_ID: Optional[str] = os.getenv("HYPERCLOVA_REQUEST_ID")
    
    # FAISS 벡터 스토어 설정
    VECTORSTORE_PATH: str = os.getenv(
        "VECTORSTORE_PATH", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "vectorstore", "faiss_index")
    )
    
    # 모니터링 설정
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_HEALTH_CHECK: bool = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"


# 전역 설정 인스턴스
settings = Settings()
