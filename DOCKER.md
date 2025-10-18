# Docker 가이드

이 문서는 챗봇 프로젝트의 Docker 설정 및 사용법에 대한 상세 가이드입니다.

## 🐳 Docker 설정 개요

### 컨테이너 구성
- **Backend**: FastAPI (Python 3.12) - Port 5000 (멀티스테이지 빌드, 비root 사용자)
- **Frontend**: React (Node.js 18) + Nginx - Port 3000 (프로덕션 최적화)

### 최적화 기능
- ✅ 멀티스테이지 빌드로 이미지 크기 최소화
- ✅ 비root 사용자로 보안 강화
- ✅ 헬스체크 및 모니터링 지원
- ✅ 개발/프로덕션 환경 분리
- ✅ 네트워크 격리 및 볼륨 최적화

## 📦 Docker 이미지 빌드

### 개별 이미지 빌드

#### 백엔드 이미지 빌드
```bash
# 백엔드 디렉토리에서
cd backend
docker build -t chatbot-backend .

# 또는 루트 디렉토리에서
docker build -t chatbot-backend ./backend
```

#### 프론트엔드 이미지 빌드
```bash
# 프론트엔드 디렉토리에서
cd frontend
docker build -t chatbot-frontend .

# 또는 루트 디렉토리에서
docker build -t chatbot-frontend ./frontend
```

### 전체 스택 빌드 (Docker Compose)
```bash
# 전체 스택 빌드 및 실행
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 캐시 없이 강제 빌드
docker-compose build --no-cache
```

## 🚀 컨테이너 실행

### Docker Compose 사용 (권장)

#### 전체 스택 실행
```bash
# 개발 모드 (볼륨 마운트 포함)
docker-compose up

# 프로덕션 모드
docker-compose -f docker-compose.yml up -d
```

#### 개별 서비스 실행
```bash
# 백엔드만 실행
docker-compose up backend

# 프론트엔드만 실행
docker-compose up frontend

# 특정 서비스 재시작
docker-compose restart backend
```

### 직접 Docker 명령어 사용

#### 백엔드 컨테이너 실행
```bash
# 기본 실행
docker run -d -p 5000:5000 --name chatbot-backend chatbot-backend

# 환경 변수와 함께 실행
docker run -d -p 5000:5000 \
  -e PYTHONUNBUFFERED=1 \
  --name chatbot-backend \
  chatbot-backend

# 볼륨 마운트와 함께 실행 (개발용)
docker run -d -p 5000:5000 \
  -v $(pwd)/backend:/app \
  --name chatbot-backend \
  chatbot-backend
```

#### 프론트엔드 컨테이너 실행
```bash
# 기본 실행
docker run -d -p 3000:3000 --name chatbot-frontend chatbot-frontend

# 환경 변수와 함께 실행
docker run -d -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:5000 \
  --name chatbot-frontend \
  chatbot-frontend
```

## 🔧 Docker Compose 설정

### 기본 설정 (docker-compose.yml)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
      - ENVIRONMENT=development
    volumes:
      - ./backend:/app
      - backend_cache:/app/.cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - chatbot-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:5000
      - NODE_ENV=production
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - chatbot-network

volumes:
  backend_cache:
    driver: local

networks:
  chatbot-network:
    driver: bridge
```

### 프로덕션용 설정 (docker-compose.prod.yml)
```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/${GITHUB_REPOSITORY}/backend:latest
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
      - ENVIRONMENT=production
      - BACKEND_HOST=0.0.0.0
      - BACKEND_PORT=5000
    restart: always
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - chatbot-network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  frontend:
    image: ghcr.io/${GITHUB_REPOSITORY}/frontend:latest
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:5000
      - NODE_ENV=production
    depends_on:
      backend:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - chatbot-network
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 128M
          cpus: '0.1'

networks:
  chatbot-network:
    driver: bridge
```

## 📊 컨테이너 관리

### 컨테이너 상태 확인
```bash
# 실행 중인 컨테이너 목록
docker ps

# 모든 컨테이너 목록 (중지된 것 포함)
docker ps -a

# Docker Compose 서비스 상태
docker-compose ps
```

### 로그 확인
```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs frontend

# 실시간 로그
docker-compose logs -f

# 마지막 N개 라인만 보기
docker-compose logs --tail=100 backend

# 특정 컨테이너 로그
docker logs chatbot-backend
docker logs chatbot-frontend
```

### 컨테이너 중지 및 삭제
```bash
# Docker Compose로 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v

# 개별 컨테이너 중지
docker stop chatbot-backend chatbot-frontend

# 개별 컨테이너 삭제
docker rm chatbot-backend chatbot-frontend

# 이미지 삭제
docker rmi chatbot-backend chatbot-frontend

# 사용하지 않는 이미지 일괄 삭제
docker image prune -a
```

## 🔍 디버깅 및 개발

### 컨테이너 내부 접속
```bash
# 백엔드 컨테이너 접속
docker exec -it chatbot-backend bash

# 프론트엔드 컨테이너 접속
docker exec -it chatbot-frontend sh

# Docker Compose로 접속
docker-compose exec backend bash
docker-compose exec frontend sh
```

### 환경 변수 확인
```bash
# 컨테이너 환경 변수 확인
docker exec chatbot-backend env
docker exec chatbot-frontend env
```

### 포트 포워딩 확인
```bash
# 포트 매핑 확인
docker port chatbot-backend
docker port chatbot-frontend
```

## 🌐 네트워킹

### 컨테이너 간 통신
```bash
# 같은 네트워크의 컨테이너끼리는 서비스명으로 통신 가능
# 프론트엔드에서 백엔드로: http://backend:5000
```

### 외부 네트워크 접근
```bash
# 호스트에서 컨테이너로
curl http://localhost:5000/health
curl http://localhost:3000
```

## 🔒 보안 고려사항

### 환경 변수 관리
```bash
# .env 파일 사용
echo "SECRET_KEY=your-secret-key" > .env
echo "DATABASE_URL=your-database-url" >> .env

# Docker Compose에서 .env 파일 자동 로드
docker-compose up
```

### 볼륨 권한
```bash
# 읽기 전용 볼륨 마운트
docker run -v $(pwd)/backend:/app:ro chatbot-backend
```

## 📈 성능 최적화

### 멀티스테이지 빌드 (실제 적용됨)

#### 백엔드 최적화
```dockerfile
# 멀티스테이지 빌드로 최적화
FROM python:3.12-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 프로덕션 이미지
FROM python:3.12-slim as production
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "1"]
```

#### 프론트엔드 최적화
```dockerfile
# 멀티스테이지 빌드로 최적화
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 프로덕션 이미지 (Nginx)
FROM nginx:alpine as production
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder /app/build /usr/share/nginx/html
RUN echo 'server { \
    listen 3000; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /static/ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

### 이미지 크기 최적화
```bash
# 이미지 크기 확인
docker images

# 중간 레이어 확인
docker history chatbot-backend
```

## 🚨 문제 해결

### 일반적인 문제들

#### 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :5000
netstat -tulpn | grep :3000

# 다른 포트 사용
docker-compose up -p 5001:5000
```

#### 볼륨 마운트 문제
```bash
# 볼륨 권한 확인
ls -la backend/
ls -la frontend/

# 권한 수정
chmod -R 755 backend/
chmod -R 755 frontend/
```

#### 메모리 부족
```bash
# Docker 메모리 사용량 확인
docker stats

# 메모리 제한 설정
docker run -m 512m chatbot-backend
```

### 로그 분석
```bash
# 에러 로그만 필터링
docker-compose logs backend | grep ERROR
docker-compose logs frontend | grep error

# 특정 시간대 로그
docker-compose logs --since="2024-01-01T00:00:00" backend
```

## 🔄 CI/CD 통합

### GitHub Actions에서 사용
```yaml
# .github/workflows/ci-cd.yml에서
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    push: true
    tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest
```

### 배포 스크립트
```bash
#!/bin/bash
# deploy.sh
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
docker system prune -f
```

## 🛠️ Makefile 명령어

### 기본 명령어
```bash
make help          # 모든 명령어 확인
make build         # Docker 이미지 빌드
make up            # 전체 스택 실행 (프로덕션)
make down          # 전체 스택 중지
make logs          # 로그 확인
make clean         # 사용하지 않는 Docker 리소스 정리
```

### 개발 환경
```bash
make dev           # 개발 환경 실행 (포트 3001, 5001)
make dev-down      # 개발 환경 중지
make logs-backend  # 백엔드 로그 확인
make logs-frontend # 프론트엔드 로그 확인
```

### 프로덕션 환경
```bash
make prod          # 프로덕션 환경 실행
make prod-down     # 프로덕션 환경 중지
make health        # 헬스 체크
```

### 컨테이너 관리
```bash
make shell-backend    # 백엔드 컨테이너 쉘 접속
make shell-frontend   # 프론트엔드 컨테이너 쉘 접속
make restart-backend  # 백엔드 재시작
make restart-frontend # 프론트엔드 재시작
make status          # 컨테이너 상태 확인
```

## 🌐 접속 정보

### 프로덕션 환경
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:5000
- **API 문서**: http://localhost:5000/docs

### 개발 환경
- **프론트엔드**: http://localhost:3001
- **백엔드 API**: http://localhost:5001
- **API 문서**: http://localhost:5001/docs

이 가이드를 통해 Docker 환경에서 챗봇 프로젝트를 효율적으로 관리하고 배포할 수 있습니다.
