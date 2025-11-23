# 배포 가이드 (Deployment Guide)

## 🚀 배포 방법

### 방법 1: GitHub Actions 자동 배포 (권장)

`main` 브랜치에 코드를 푸시하면 자동으로 배포됩니다.

```bash
# 1. 변경사항 커밋 및 푸시
git add .
git commit -m "배포 준비"
git push origin main

# 2. GitHub Actions가 자동으로:
#    - 테스트 실행
#    - Docker 이미지 빌드 및 푸시 (ghcr.io)
#    - AWS ECS에 배포
```

**필수 사전 설정:**
- AWS SSM Parameter Store에 환경변수 설정 필요
- GitHub Secrets에 `ROLE_ARN` 설정 필요

---

### 방법 2: Docker Compose로 수동 배포

배포 서버에서 직접 Docker Compose를 사용하여 배포합니다.

#### 1단계: 배포 서버 준비

```bash
# 배포 서버에 접속
ssh user@your-server.com

# 프로젝트 디렉토리로 이동
cd /path/to/chatbot
```

#### 2단계: 환경변수 설정

배포 서버에 `.env` 파일을 생성합니다:

```bash
# 배포 서버의 .env 파일
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

#### 3단계: Docker 이미지 가져오기

```bash
# GitHub Container Registry에서 이미지 가져오기
docker pull ghcr.io/elevensheep/chatbot/backend:latest
docker pull ghcr.io/elevensheep/chatbot/frontend:latest
```

또는 Docker Compose가 자동으로 가져옵니다.

#### 4단계: 배포 실행

```bash
# 프로덕션 환경으로 실행
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

#### 5단계: 헬스 체크

```bash
# 백엔드 헬스 체크
curl http://localhost:5000/api/health

# 프론트엔드 확인
curl http://localhost:3000
```

---

## 📋 배포 전 체크리스트

### 필수 확인 사항

- [ ] **환경변수 설정**
  - [ ] `FRONTEND_URL`이 실제 도메인으로 설정되어 있는가? (localhost 아님!)
  - [ ] `ALLOWED_ORIGINS`에 실제 도메인이 포함되어 있는가?
  - [ ] `ENVIRONMENT=production`으로 설정되어 있는가?

- [ ] **보안 설정**
  - [ ] `JWT_SECRET_KEY`가 기본값이 아닌 강력한 키인가?
  - [ ] 모든 API 키가 실제 값으로 설정되어 있는가?

- [ ] **필수 서비스**
  - [ ] MongoDB URI가 올바른가?
  - [ ] SMTP 설정이 올바른가? (Gmail 앱 비밀번호 사용)
  - [ ] HyperCLOVA API 키가 유효한가?
  - [ ] Pinecone API 키가 유효한가?

- [ ] **네트워크 설정**
  - [ ] 포트 5000, 3000이 열려있는가?
  - [ ] 방화벽 설정이 올바른가?
  - [ ] 도메인 DNS 설정이 올바른가?

---

## 🔄 업데이트 배포

기존 배포를 업데이트하려면:

```bash
# 1. 최신 이미지 가져오기
docker-compose -f docker-compose.prod.yml pull

# 2. 컨테이너 재시작
docker-compose -f docker-compose.prod.yml up -d

# 3. 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🛑 배포 중지

```bash
# 컨테이너 중지
docker-compose -f docker-compose.prod.yml down

# 컨테이너와 볼륨 모두 삭제 (주의!)
docker-compose -f docker-compose.prod.yml down -v
```

---

## 📊 모니터링

### 로그 확인

```bash
# 모든 로그
docker-compose -f docker-compose.prod.yml logs -f

# 백엔드만
docker-compose -f docker-compose.prod.yml logs -f backend

# 프론트엔드만
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 상태 확인

```bash
# 컨테이너 상태
docker-compose -f docker-compose.prod.yml ps

# 리소스 사용량
docker stats
```

---

## ⚠️ 문제 해결

### 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 환경변수 확인
docker-compose -f docker-compose.prod.yml config

# 컨테이너 재빌드
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### 환경변수 오류

```bash
# .env 파일 확인
cat .env

# 환경변수가 제대로 로드되는지 확인
docker-compose -f docker-compose.prod.yml config | grep -A 5 environment
```

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
netstat -tulpn | grep :5000
netstat -tulpn | grep :3000

# 기존 컨테이너 중지
docker-compose -f docker-compose.prod.yml down
```

---

## 🔐 보안 주의사항

1. **`.env` 파일은 절대 Git에 커밋하지 마세요!**
   - `.gitignore`에 이미 포함되어 있습니다.

2. **프로덕션에서는 강력한 `JWT_SECRET_KEY` 사용**
   - 기본값 `dev-jwt-secret-key-change-me` 사용 금지

3. **API 키는 안전하게 관리**
   - 환경변수나 Secret Manager 사용 권장

4. **HTTPS 사용 권장**
   - 프로덕션에서는 HTTPS를 사용하는 것이 좋습니다.
   - 현재는 HTTP로 설정되어 있지만, 나중에 HTTPS로 변경 가능합니다.

