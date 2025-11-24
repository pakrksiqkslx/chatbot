# Docker 이미지 배포 시 환경변수 설정 가이드

## 배포 서버에서 환경변수 설정 방법

Docker 이미지를 배포할 때는 **배포 서버**에서 환경변수를 설정해야 합니다.

### 방법 1: .env 파일 사용 (권장)

배포 서버에 `.env` 파일을 생성하거나, `docker-compose.prod.yml`과 같은 디렉토리에 `.env` 파일을 만듭니다:

```bash
# 배포 서버의 .env 파일 (프로덕션용)
# ============================================
# 필수 API 키
# ============================================
HYPERCLOVA_API_KEY=실제-하이퍼클로바-API-키
PINECONE_API_KEY=실제-파인콘-API-키
PINECONE_INDEX_NAME=chatbot-courses

# ============================================
# 필수 데이터베이스 설정
# ============================================
MONGODB_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/
MONGODB_DATABASE=chatbot_db

# ============================================
# 필수 이메일 설정
# ============================================
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# ============================================
# 보안 설정
# ============================================
JWT_SECRET_KEY=강력한-랜덤-문자열-프로덕션용

# ============================================
# 배포 환경 설정 (중요!)
# ============================================
ENVIRONMENT=production
FRONTEND_URL=http://bu-chatbot.co.kr
ALLOWED_ORIGINS=http://bu-chatbot.co.kr

# ============================================
# 서버 설정 (선택사항)
# ============================================
PORT=5000
BACKEND_PORT=5000
BACKEND_HOST=0.0.0.0
LOG_LEVEL=INFO
DEBUG=false
```

### 방법 2: 환경변수 직접 설정

배포 서버에서 환경변수를 직접 설정:

```bash
export FRONTEND_URL=https://bu-chatbot.co.kr
export ALLOWED_ORIGINS=http://bu-chatbot.co.kr,https://bu-chatbot.co.kr
export ENVIRONMENT=production
export HYPERCLOVA_API_KEY=실제-키
export PINECONE_API_KEY=실제-키
export MONGODB_URI=mongodb+srv://...
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export JWT_SECRET_KEY=강력한-키

# docker-compose 실행
docker-compose -f docker-compose.prod.yml up -d
```

### 방법 3: docker-compose.prod.yml 수정

`docker-compose.prod.yml` 파일의 `environment` 섹션에 직접 값을 입력 (보안상 권장하지 않음):

```yaml
environment:
  - FRONTEND_URL=https://bu-chatbot.co.kr
  - ALLOWED_ORIGINS=http://bu-chatbot.co.kr,https://bu-chatbot.co.kr
  # ... 기타 환경변수
```

## 중요: 로컬 vs 배포 환경 구분

### 로컬 개발 환경 (.env 파일)
```bash
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
ENVIRONMENT=development
```

### 배포 환경 (배포 서버의 .env 또는 환경변수)
```bash
FRONTEND_URL=http://bu-chatbot.co.kr
ALLOWED_ORIGINS=http://bu-chatbot.co.kr
ENVIRONMENT=production
```

## 배포 체크리스트

배포 전 다음 사항을 확인하세요:

- [ ] `FRONTEND_URL`이 실제 도메인으로 설정되어 있는가? (localhost 아님!)
- [ ] `ALLOWED_ORIGINS`에 실제 도메인이 포함되어 있는가?
- [ ] `ENVIRONMENT=production`으로 설정되어 있는가?
- [ ] `JWT_SECRET_KEY`가 기본값이 아닌 강력한 키인가?
- [ ] 모든 필수 API 키가 설정되어 있는가?
- [ ] MongoDB URI가 올바른가?
- [ ] SMTP 설정이 올바른가?

## docker-compose.prod.yml 동작 방식

`docker-compose.prod.yml`은 다음과 같이 동작합니다:

```yaml
- FRONTEND_URL=${FRONTEND_URL:-https://bu-chatbot.co.kr}
```

이 의미는:
- 환경변수 `FRONTEND_URL`이 있으면 그 값을 사용
- 없으면 기본값 `https://bu-chatbot.co.kr` 사용

따라서 배포 서버에서 `.env` 파일이나 환경변수로 `FRONTEND_URL`을 설정하면 그 값이 사용되고,
설정하지 않으면 기본값이 사용됩니다.

## 배포 명령어 예시

```bash
# 1. .env 파일 생성 (배포 서버에서)
nano .env  # 위의 배포 환경 설정 내용 입력

# 2. Docker Compose로 배포
docker-compose -f docker-compose.prod.yml pull  # 최신 이미지 가져오기
docker-compose -f docker-compose.prod.yml up -d  # 백그라운드 실행

# 3. 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

