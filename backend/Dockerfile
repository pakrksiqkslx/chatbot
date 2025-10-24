# AWS Lambda용 Python 이미지 사용
FROM public.ecr.aws/lambda/python:3.12

# 작업 디렉토리 설정
WORKDIR ${LAMBDA_TASK_ROOT}

# 시스템 패키지 업데이트 및 빌드 도구 설치
RUN microdnf update -y && \
    microdnf install -y gcc gcc-c++ && \
    microdnf clean all

# Python 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# HuggingFace 캐시 디렉토리 설정
ENV HF_HOME=/tmp/.cache/huggingface
ENV TRANSFORMERS_CACHE=/tmp/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/.cache/sentence-transformers

# 캐시 디렉토리 생성
RUN mkdir -p /tmp/.cache/huggingface /tmp/.cache/sentence-transformers

# 애플리케이션 코드 복사
COPY . .

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]
