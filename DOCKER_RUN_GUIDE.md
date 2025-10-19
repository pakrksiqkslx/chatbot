# 🐳 Docker로 챗봇 실행하기

## 📋 사전 준비

### 1. Docker 설치 확인

```bash
docker --version
docker-compose --version
```

**Docker Desktop이 설치되어 있지 않다면:**
- Windows: https://docs.docker.com/desktop/install/windows-install/
- 설치 후 재부팅 필요

### 2. 벡터스토어 생성 확인

```bash
# vectorstore 폴더가 존재하는지 확인
ls vectorstore/faiss_index/
```

**벡터스토어가 없다면:**
```bash
python vectorize_courses.py
```

---

## 🚀 Docker로 실행하기

### 방법 1: docker-compose로 전체 실행 (권장) ⭐

```bash
# 프로젝트 루트에서 실행
docker-compose up --build
```

**실행되는 서비스:**
- ✅ Backend API (포트 5000)
- ✅ Frontend (포트 3000)

**접속 URL:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/docs

**종료:**
```bash
Ctrl + C  # 또는
docker-compose down
```

---

### 방법 2: 백그라운드 실행

```bash
# 백그라운드로 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 특정 서비스만 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 종료
docker-compose down
```

---

### 방법 3: 개발 모드 실행 (코드 변경 시 자동 재시작)

```bash
# 개발 모드 프로필로 실행
docker-compose --profile dev up --build
```

**개발 모드 특징:**
- ✅ 코드 변경 시 자동 재시작 (Hot Reload)
- ✅ 볼륨 마운트로 실시간 반영
- Backend Dev: http://localhost:5001
- Frontend Dev: http://localhost:3001

---

## 📊 실행 확인

### 1. 컨테이너 상태 확인

```bash
docker-compose ps
```

**정상 실행 시:**
```
NAME                 STATUS              PORTS
chatbot-backend-1    Up (healthy)        0.0.0.0:5000->5000/tcp
chatbot-frontend-1   Up (healthy)        0.0.0.0:3000->3000/tcp
```

### 2. 헬스 체크

```bash
# 백엔드 헬스 체크
curl http://localhost:5000/health

# 프론트엔드 접속
curl http://localhost:3000
```

### 3. 로그 확인

```bash
# 모든 서비스 로그
docker-compose logs -f

# 백엔드만
docker-compose logs -f backend

# 프론트엔드만
docker-compose logs -f frontend
```

---

## 🔧 환경 변수 설정

`.env` 파일을 만들어서 환경 변수를 관리할 수 있습니다:

```bash
# .env 파일 생성
cat > .env << EOF
# HyperCLOVA X API
HYPERCLOVA_API_KEY=nv-93ec8a8d596946b2b2314d70dcdba676qLCw
HYPERCLOVA_REQUEST_ID=

# 서버 설정
BACKEND_PORT=5000
FRONTEND_PORT=3000

# 환경
ENVIRONMENT=production
DEBUG=false
EOF
```

그리고 `docker-compose.yml`에서:

```yaml
services:
  backend:
    env_file:
      - .env
```

---

## 🛠️ 유용한 Docker 명령어

### 빌드만 실행
```bash
docker-compose build
```

### 특정 서비스만 실행
```bash
# 백엔드만
docker-compose up backend

# 프론트엔드만
docker-compose up frontend
```

### 컨테이너 재시작
```bash
docker-compose restart

# 특정 서비스만
docker-compose restart backend
```

### 컨테이너 접속 (디버깅)
```bash
# 백엔드 컨테이너 접속
docker-compose exec backend /bin/bash

# 프론트엔드 컨테이너 접속
docker-compose exec frontend /bin/sh
```

### 이미지 삭제 및 재빌드
```bash
# 모든 컨테이너, 볼륨 삭제
docker-compose down -v

# 이미지 삭제
docker-compose down --rmi all

# 완전히 새로 빌드
docker-compose up --build --force-recreate
```

---

## 🐛 문제 해결

### 1. 포트 충돌

**오류:** `port is already allocated`

**해결:**
```bash
# 포트 변경 (docker-compose.yml)
ports:
  - "8000:5000"  # 5000 대신 8000 사용
```

### 2. 빌드 실패

**오류:** `ERROR [internal] load metadata`

**해결:**
```bash
# Docker Desktop 재시작
# 또는
docker system prune -a
docker-compose build --no-cache
```

### 3. 벡터스토어 로드 실패

**오류:** `벡터 스토어를 찾을 수 없습니다`

**해결:**
```bash
# 벡터스토어 생성
python vectorize_courses.py

# 경로 확인
ls vectorstore/faiss_index/
```

### 4. 메모리 부족

**오류:** `Killed` 또는 `Out of memory`

**해결:**
- Docker Desktop 설정에서 메모리 할당 증가 (최소 4GB 권장)
- Settings > Resources > Memory 조정

---

## 📂 Docker 파일 구조

```
chatbot/
├── docker-compose.yml          # 전체 서비스 오케스트레이션
├── docker-compose.prod.yml     # 프로덕션 설정
├── backend/
│   ├── Dockerfile              # 백엔드 Docker 이미지
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile              # 프론트엔드 Docker 이미지
│   └── package.json
└── vectorstore/                # 벡터스토어 (마운트됨)
    └── faiss_index/
```

---

## 🎯 권장 실행 순서

### 1단계: 벡터스토어 생성 (최초 1회)

```bash
python vectorize_courses.py
```

### 2단계: Docker 빌드 및 실행

```bash
docker-compose up --build
```

### 3단계: 브라우저 접속

http://localhost:3000

---

## 🔄 프로덕션 배포

프로덕션 환경:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 💡 팁

### 빠른 재시작

개발 중에 코드를 수정했을 때:

```bash
# 백엔드만 재시작
docker-compose restart backend

# 프론트엔드만 재시작
docker-compose restart frontend
```

### 리소스 정리

```bash
# 사용하지 않는 이미지, 컨테이너 삭제
docker system prune -a

# 볼륨까지 모두 삭제
docker system prune -a --volumes
```

---

## ✅ 실행 체크리스트

- [ ] Docker Desktop 실행 중
- [ ] `vectorstore/faiss_index/` 존재
- [ ] API 키 설정됨
- [ ] `docker-compose up --build` 실행
- [ ] http://localhost:3000 접속
- [ ] 챗봇 질문 테스트

---

## 📞 문의

문제 발생 시:
1. 로그 확인: `docker-compose logs -f`
2. 컨테이너 상태: `docker-compose ps`
3. 헬스 체크: `curl http://localhost:5000/health`

