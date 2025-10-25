# 멀티스테이지 빌드로 최적화
FROM public.ecr.aws/lambda/python:3.12 AS base

# 작업 디렉토리 설정
WORKDIR ${LAMBDA_TASK_ROOT}

# Python 의존성 파일만 먼저 복사 (캐시 최적화)
COPY requirements.txt .

# 의존성 설치 최적화
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# 애플리케이션 코드 복사
COPY . .

# 불필요한 파일 제거 (Lambda 환경에 맞게 최적화)
RUN rm -rf __pycache__ && \
    rm -rf .git && \
    rm -rf *.egg-info && \
    rm -rf .pytest_cache && \
    rm -rf .mypy_cache && \
    rm -rf .coverage && \
    rm -rf *.pyc && \
    rm -rf *.pyo && \
    rm -rf *.pyd

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]
