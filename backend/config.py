"""
애플리케이션 설정 관리
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드 (backend/.env 또는 프로젝트 루트의 .env)
backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).parent.parent / ".env"

if backend_env.exists():
    try:
        load_dotenv(backend_env, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            load_dotenv(backend_env, encoding='utf-16')
        except:
            pass  # .env 파일을 읽을 수 없으면 환경변수에서 직접 읽음
elif root_env.exists():
    try:
        load_dotenv(root_env, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            load_dotenv(root_env, encoding='utf-16')
        except:
            pass  # .env 파일을 읽을 수 없으면 환경변수에서 직접 읽음


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
    HYPERCLOVA_API_KEY: str = os.getenv("HYPERCLOVA_API_KEY", "")
    HYPERCLOVA_API_GATEWAY_KEY: Optional[str] = os.getenv("HYPERCLOVA_API_GATEWAY_KEY")
    HYPERCLOVA_REQUEST_ID: Optional[str] = os.getenv("HYPERCLOVA_REQUEST_ID")
    
    # 벡터 스토어 설정 (PINECONE 우선, FAISS 폴백)
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "chatbot-courses")
    
    # FAISS 벡터 스토어 설정 (폴백용)
    VECTORSTORE_PATH: str = os.getenv(
        "VECTORSTORE_PATH", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "vectorstore", "faiss_index")
    )
    
    # 벡터 스토어 타입 설정
    USE_PINECONE: bool = os.getenv("USE_PINECONE", "true").lower() == "true"
    
    # 모니터링 설정
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_HEALTH_CHECK: bool = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"


# 전역 설정 인스턴스
settings = Settings()
