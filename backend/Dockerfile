# ECS용 경량 Python 이미지 사용
FROM python:3.12-slim

# 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 (필요시 추가)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출 (config 기본 5000)
EXPOSE 5000

# Uvicorn으로 FastAPI 실행 (ECS 환경변수로 포트/워커/로그레벨 제어)
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT:-5000} --workers ${BACKEND_WORKERS:-1} --log-level ${LOG_LEVEL:-info}"]
