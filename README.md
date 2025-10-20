# 수업계획서 기반 맞춤형 학습 지원 챗봇

<br>

## 📚 프로젝트 소개

**수업계획서 기반 맞춤형 학습 지원 챗봇**은 Naver의 HyperCLOVA X LLM을 기반으로, 강의 계획서를 미세조정(Fine-tuning)하여 학생들에게 해당 수업에 대한 정보를 정확하고 신속하게 제공하는 웹 서비스입니다.

학생들이 강의 정보를 얻기 위해 겪는 번거로움을 줄이고, 교직원의 반복적인 응대 업무를 자동화하여 교육 환경의 전반적인 효율성을 높이는 것을 목표로 합니다.

<br>

## ✨ 주요 기능

| 기능 | 상세 내용 |
| :--- | :--- |
| **챗봇 구현** | • 수업계획서 기반의 질의응답 기능<br>• 학생 질의응답 챗봇으로 정보 접근성 향상 |
| **한국어 LLM** | • 한국어에 특화된 **HyperCLOVA X SEED** LLM 사용<br>• 도메인(수업계획서) 데이터에 대한 QA 최적화 |
| **벡터 검색** | • 정보 조회 기능의 정확성 강화<br>• 질문과 의미적으로 유사한 문서를 기반으로 정확한 답변 제공 |

<br>

## 🎯 프로젝트 목적

1.  **접근성 향상**: 분산된 수업 정보를 통합하여 언제든지 쉽게 검색하고 접근할 수 있도록 합니다.
2.  **시간 절약**: 반복적인 질문에 대한 응답을 자동화하여 학생들의 대기 시간을 단축하고, 교직원의 업무 부담을 경감시킵니다.
3.  **정확한 정보 제공**: 한국어에 특화된 LLM과 벡터 DB를 결합하여, 사용자의 질문 의도를 정확히 파악하고 신뢰도 높은 답변을 생성합니다.

<br>

## 🛠️ 개발 환경 (Tech Stack)

### Frontend
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

### DBMS
![Pinecone](https://img.shields.io/badge/Pinecone-0C55C3?style=for-the-badge&logo=pinecone&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

### LLM
![LLM](https://img.shields.io/badge/HyperCLOVA%20X-03C75A?style=for-the-badge&logo=naver&logoColor=white)

### Library
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-FF69B4?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-4A90E2?style=for-the-badge)
![Tesseract](https://img.shields.io/badge/Tesseract-4A90E2?style=for-the-badge)

### Collaboration Tools
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white)

<br>

## ⚙️ 시스템 아키텍처

본 프로젝트는 **OCR 데이터 처리 흐름**과 **LLM 질의응답 흐름** 두 가지 핵심 파트로 구성됩니다.

### 1. OCR Flow Chart (데이터 처리)

1.  **수업계획서 PDF 수집**: 학교 및 교육기관으로부터 수업계획서 PDF 파일을 수집합니다.
2.  **PDF 유효성 검사**: 수집된 PDF가 텍스트 기반인지 이미지 기반인지 판별합니다.
3.  **OCR 처리**: 이미지 기반의 PDF일 경우, `PyMuPDF`와 `Tesseract`를 이용해 텍스트를 추출합니다.
4.  **텍스트 데이터 저장**: 추출된 텍스트 데이터를 정제하여 저장합니다.

### 2. LLM Flow Chart (모델 및 응답)

1.  **데이터 벡터화**: 정제된 텍스트 데이터를 임베딩 모델을 통해 벡터로 변환합니다.
2.  **LLM 미세조정**: 변환된 벡터 데이터로 `HyperCLOVA X SEED` 모델을 미세조정하여 도메인 특화 LLM을 생성합니다.
3.  **벡터 DB 저장**: 생성된 벡터를 `Pinecone` 또는 `FAISS` 벡터 DB에 저장하고 인덱싱합니다.
4.  **사용자 질문 입력**: 사용자가 챗봇 인터페이스를 통해 질문을 입력합니다.
5.  **유사 문서 검색**: 사용자 질문을 벡터로 변환한 후, 벡터 DB에서 코사인 유사도가 가장 높은 문서를 검색합니다.
6.  **맞춤형 답변 생성**: 검색된 문서와 사용자 질문을 프롬프트로 구성하여 미세조정된 LLM에게 전달하고, 최종 답변을 생성하여 사용자에게 제공합니다.

<br>

## 🚀 시작하기

### 사전 준비

-   Docker Desktop 설치 및 실행
-   Git 설치

### ⚡ 팀원용 초간단 실행 (권장)

```bash
# 1. 클론
git clone https://github.com/ley38107/chatbot.git
cd chatbot

# 2. 자동 설정 및 실행
setup-for-team.bat
```

**끝!** 🎉 브라우저에서 http://localhost:3000 접속

### 🔧 수동 설정 방법

1.  **프로젝트 클론**
    ```sh
    git clone https://github.com/ley38107/chatbot.git
    cd chatbot
    ```

2.  **Frontend 설정**
    ```sh
    cd frontend
    npm install
    npm start
    ```

3.  **Backend 설정**
    ```sh
    cd backend
    pip install -r requirements.txt
    ```

4.  **환경변수 설정**
    프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 채워주세요.
    
    **PINECONE 사용 (권장):**
    ```env
    PINECONE_API_KEY=your-pinecone-api-key-here
    HYPERCLOVA_API_KEY=your-hyperclova-api-key-here
    USE_PINECONE=true
    ```
    
    **FAISS 사용 (폴백):**
    ```env
    HYPERCLOVA_API_KEY=your-hyperclova-api-key-here
    USE_PINECONE=false
    ```
    
    **API 키 발급 방법:**
    - **PINECONE**: https://www.pinecone.io/ → API Keys
    - **HyperCLOVA X**: https://clovastudio.ncloud.com/ → 새 앱 생성

5.  **벡터화 (FAISS 사용 시만)**
    ```sh
    python vectorize_courses.py
    ```

6.  **Docker로 실행 (권장)**
    ```sh
    docker-start.bat
    ```
    
    **또는 수동 실행:**
    ```sh
    uvicorn main:app --reload
    ```

<br>

## 🧑‍💻 팀원 (9팀)

| 이름 | 역할 |
| :--- | :--- |
| **이희재** | PM |
| **김성수** | BE |
| **이정욱** | BE |
| **박성빈** | FE |
