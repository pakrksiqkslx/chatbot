# AWS Lambda용 Python 이미지 사용
FROM public.ecr.aws/lambda/python:3.12

# 작업 디렉토리 설정
WORKDIR ${LAMBDA_TASK_ROOT}

# Python 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치 (Lambda 호환성을 위해 단순화)
RUN pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]
