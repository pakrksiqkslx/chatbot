# 🤖 HyperCLOVA X API 설정 가이드

## 📋 API 키 발급 방법

### 1. CLOVA Studio 접속
https://clovastudio.ncloud.com/

### 2. 로그인 및 앱 생성
1. 네이버 클라우드 계정으로 로그인
2. **새 앱 만들기** 클릭
3. 앱 이름 입력 (예: `chatbot-app`)
4. 모델 선택: **HyperCLOVA X**

### 3. API 키 발급
1. 생성한 앱 선택
2. **API Key** 탭 이동
3. **API Key 생성** 클릭
4. 생성된 키 복사

---

## 🔧 설정 방법

### 1. API 키 및 엔드포인트 확인

CLOVA Studio에서 다음 정보를 확인하세요:

```
App ID: testapp (예시, 실제로는 본인의 앱 ID)
API Key: clovastudio_xxxxxxxxxxxxxxxxxxxxxxxx
API Gateway Key: xxxx-xxxx-xxxx-xxxx (선택사항)
```

### 2. config.py 수정

`backend/config.py`에서 다음 정보를 수정하세요:

```python
# 외부 API 설정 - HyperCLOVA X
HYPERCLOVA_API_KEY: str = os.getenv("HYPERCLOVA_API_KEY", "여기에_발급받은_API_키_입력")
HYPERCLOVA_API_GATEWAY_KEY: Optional[str] = os.getenv("HYPERCLOVA_API_GATEWAY_KEY")
HYPERCLOVA_REQUEST_ID: Optional[str] = os.getenv("HYPERCLOVA_REQUEST_ID")
```

### 3. hyperclova_client.py의 API URL 수정

`backend/hyperclova_client.py` 18번 줄:

```python
# testapp을 본인의 App ID로 변경
API_URL = "https://clovastudio.apigw.ntruss.com/[본인의_앱_ID]/v1/chat-completions/HCX-003"
```

예시:
```python
API_URL = "https://clovastudio.apigw.ntruss.com/my-chatbot-app/v1/chat-completions/HCX-003"
```

---

## 📡 API 형식 (표준)

### 요청 (Request)

```http
POST https://clovastudio.apigw.ntruss.com/[APP_ID]/v1/chat-completions/HCX-003
Content-Type: application/json
Authorization: Bearer [API_KEY]
```

```json
{
  "messages": [
    {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
    {"role": "user", "content": "안녕하세요"}
  ],
  "topP": 0.8,
  "topK": 0,
  "maxTokens": 500,
  "temperature": 0.5,
  "repetitionPenalty": 1.1,
  "stop": [],
  "seed": 0,
  "includeAiFilters": true
}
```

### 응답 (Response)

```json
{
  "status": {
    "code": "20000",
    "message": "OK"
  },
  "result": {
    "message": {
      "role": "assistant",
      "content": "안녕하세요! 무엇을 도와드릴까요?"
    },
    "usage": {
      "promptTokens": 15,
      "completionTokens": 10,
      "totalTokens": 25
    }
  }
}
```

---

## ✅ Mock 모드 해제

API 키 설정 후 실제 HyperCLOVA X를 사용하려면:

`backend/hyperclova_client.py` 132번 줄 수정:

```python
# Mock 모드 (현재)
if True:  # Mock 사용
    logger.info("Mock 응답 생성 중 (API 키 문제로 임시 사용)")
    return self._generate_mock_answer(query, context_docs)

# 실제 API 사용 (변경)
if False:  # Mock 사용 안 함
    logger.info("Mock 응답 생성 중 (API 키 문제로 임시 사용)")
    return self._generate_mock_answer(query, context_docs)
```

---

## 🧪 테스트

### 1. 백엔드 재시작

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### 2. 테스트 실행

```bash
python test_chat.py
```

### 3. 로그 확인

성공 시:
```
HyperCLOVA X API 호출 중... (메시지 수: 2)
HyperCLOVA X API 호출 성공
```

실패 시:
```
HyperCLOVA X API 호출 실패: 401 Client Error
응답 내용: {"status":{"code":"40104","message":"..."}}
```

---

## 🔍 문제 해결

### 1. 401 Unauthorized

**원인**: API 키가 잘못되었거나 형식이 맞지 않음

**해결**:
- CLOVA Studio에서 새 API 키 발급
- `config.py`에 정확한 API 키 입력
- API URL의 App ID 확인

### 2. 404 Not Found

**원인**: API URL이 잘못됨

**해결**:
- App ID가 정확한지 확인
- 엔드포인트 경로 확인: `/v1/chat-completions/HCX-003`

### 3. 400 Bad Request

**원인**: 요청 형식이 잘못됨

**해결**:
- 로그에서 요청 페이로드 확인
- API 스펙과 비교

---

## 📊 API 파라미터 설명

| 파라미터 | 타입 | 범위 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `maxTokens` | int | - | 500 | 최대 생성 토큰 수 |
| `temperature` | float | 0.00~1.00 | 0.5 | 다양성 (높을수록 창의적) |
| `topP` | float | 0~1 | 0.8 | 누적 확률 샘플링 |
| `topK` | int | 0~128 | 0 | Top-K 샘플링 |
| `repetitionPenalty` | float | 0.0~2.0 | 1.1 | 반복 방지 |
| `seed` | int | 0~4294967295 | 0 | 일관성 수준 |

---

## 💡 추천 설정

### 일반 대화

```python
temperature=0.7
top_p=0.8
repetition_penalty=1.1
```

### 정확한 정보 제공

```python
temperature=0.3
top_p=0.6
repetition_penalty=1.2
```

### 창의적 답변

```python
temperature=0.9
top_p=0.9
repetition_penalty=1.0
```

---

## 🔗 참고 자료

- [CLOVA Studio 공식 문서](https://guide.ncloud-docs.com/docs/clovastudio-overview)
- [HyperCLOVA X API 가이드](https://guide.ncloud-docs.com/docs/clovastudio-api-guide)
- [API 레퍼런스](https://api.ncloud-docs.com/docs/ai-application-service-clovastudio)

