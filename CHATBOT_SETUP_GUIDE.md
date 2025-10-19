# 🤖 수업계획서 챗봇 설정 및 실행 가이드

## 🎯 시스템 아키텍처

```
사용자 질문
    ↓
FastAPI 서버 (/chat 엔드포인트)
    ↓
FAISS 벡터 검색 (유사 문서 3개 검색)
    ↓
HyperCLOVA X API (컨텍스트 기반 답변 생성)
    ↓
사용자에게 답변 반환
```

---

## 📋 사전 준비

### 1. 벡터화 완료 확인

벡터 스토어가 생성되어 있어야 합니다:
```
vectorstore/
├── faiss_index/
│   ├── index.faiss
│   └── index.pkl
└── metadata_stats.json
```

**아직 벡터화를 하지 않았다면:**
```bash
python vectorize_courses.py
```

### 2. HyperCLOVA X API 키

- ✅ API 키: `nv-ad983799a6a840afa1f9b3086a81406e1UEy`
- 이미 `backend/config.py`에 설정되어 있습니다.

---

## 🚀 실행 방법

### 1단계: 백엔드 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

**설치 시간:** 약 3-5분 (임베딩 모델 다운로드 포함)

### 2단계: 서버 실행

```bash
cd backend
python main.py
```

또는:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

**서버 실행 확인:**
- 서버 주소: http://localhost:5000
- API 문서: http://localhost:5000/docs
- 헬스 체크: http://localhost:5000/health

---

## 🧪 테스트

### 방법 1: 테스트 스크립트 실행

```bash
cd backend
python test_chat.py
```

### 방법 2: curl 명령어

```bash
# 헬스 체크
curl http://localhost:5000/health

# 챗봇 질문
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "C언어프로그래밍 교수님 누구야?",
    "k": 3,
    "include_sources": true
  }'
```

### 방법 3: API 문서 (Swagger UI)

1. 브라우저에서 http://localhost:5000/docs 접속
2. `/chat` 엔드포인트 클릭
3. "Try it out" 클릭
4. 요청 본문 입력:
   ```json
   {
     "query": "C언어프로그래밍 교수님 누구야?",
     "k": 3,
     "include_sources": true
   }
   ```
5. "Execute" 클릭

---

## 📡 API 사용법

### POST `/chat`

**요청 본문:**
```json
{
  "query": "사용자 질문",
  "k": 3,                    // 검색할 문서 수 (기본값: 3)
  "include_sources": true    // 출처 포함 여부 (기본값: true)
}
```

**응답 예시:**
```json
{
  "answer": "C언어프로그래밍은 정원석 교수님이 담당하고 계십니다.",
  "sources": [
    {
      "course_name": "[0367001]C언어프로그래밍",
      "professor": "정원석",
      "section": "교과목 운영",
      "score": 0.234,
      "content_preview": "[강의명] C언어프로그래밍\n[담당교수] 정원석..."
    }
  ]
}
```

---

## 🔧 설정 변경

### 환경 변수 설정

`backend/.env` 파일을 생성하여 설정을 변경할 수 있습니다:

```bash
# 환경 설정
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# 서버 설정
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000

# HyperCLOVA X API 설정
HYPERCLOVA_API_KEY=your-api-key-here

# FAISS 벡터 스토어 설정
VECTORSTORE_PATH=../vectorstore/faiss_index

# CORS 설정
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 답변 품질 조정

`backend/hyperclova_client.py`의 `generate_answer()` 함수에서:

```python
# 답변 길이 조정
max_tokens=500  # 기본값, 더 길게: 1000

# 답변 창의성 조정
temperature=0.3  # 낮을수록 일관적, 높을수록 창의적 (0.0~1.0)

# 반복 방지
repeat_penalty=1.2  # 높을수록 반복 감소
```

---

## 🐛 문제 해결

### 1. 서버 실행 오류

**오류:** `ModuleNotFoundError`
```bash
# 패키지 재설치
cd backend
pip install -r requirements.txt
```

**오류:** `벡터 스토어를 찾을 수 없습니다`
```bash
# 벡터화 실행
python vectorize_courses.py
```

### 2. HyperCLOVA X API 오류

**오류:** `API 호출 실패 401`
- API 키를 확인하세요
- `backend/config.py`의 `HYPERCLOVA_API_KEY` 확인

**오류:** `API 호출 실패 429 (Too Many Requests)`
- API 호출 제한 초과
- 잠시 후 다시 시도

### 3. 메모리 부족

벡터 스토어 로딩 시 메모리 부족:
```python
# vectorstore_service.py에서
model_kwargs={'device': 'cpu'}  # GPU 사용 시 'cuda'로 변경
```

---

## 📊 성능 최적화

### 검색 속도 향상

```python
# 검색 문서 수 줄이기
k=2  # 기본값 3 → 2로 감소
```

### 답변 생성 속도 향상

```python
# HyperCLOVA X 토큰 수 줄이기
max_tokens=300  # 기본값 500 → 300으로 감소
```

---

## 🔄 프론트엔드 연동

React 프론트엔드에서 API 호출:

```javascript
async function sendMessage(query) {
  const response = await fetch('http://localhost:5000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      k: 3,
      include_sources: true
    })
  });
  
  const data = await response.json();
  return data;
}
```

---

## 📝 다음 단계

1. ✅ 백엔드 서버 실행
2. ✅ API 테스트
3. ⬜ 프론트엔드 연동
4. ⬜ 사용자 인증 추가
5. ⬜ 대화 히스토리 저장
6. ⬜ 프로덕션 배포

---

## 💡 추가 기능 아이디어

- [ ] 대화 컨텍스트 유지 (이전 대화 기억)
- [ ] 다중 파일 업로드 지원
- [ ] 교수별/과목별 필터링
- [ ] 음성 인식/TTS 추가
- [ ] 피드백 시스템 (답변 평가)

---

## 📞 문의

문제가 발생하면 로그를 확인하세요:
```bash
# 서버 로그 확인
tail -f backend.log
```

