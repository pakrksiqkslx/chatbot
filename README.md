# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

1.  **수업계획서 PDF 수집**: 학교 및 교육기관으로부터 수업계획서 PDF 파일을 수집합니다.
2.  **PDF 유효성 검사**: 수집된 PDF가 텍스트 기반인지 이미지 기반인지 판별합니다.
3.  **OCR 처리**: 이미지 기반의 PDF일 경우, `PyMuPDF`와 `Tesseract`를 이용해 텍스트를 추출합니다.
4.  **텍스트 데이터 저장**: 추출된 텍스트 데이터를 정제하여 저장합니다.

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration
1.  **데이터 벡터화**: 정제된 텍스트 데이터를 임베딩 모델을 통해 벡터로 변환합니다.
2.  **LLM 미세조정**: 변환된 벡터 데이터로 `HyperCLOVA X SEED` 모델을 미세조정하여 도메인 특화 LLM을 생성합니다.
3.  **벡터 DB 저장**: 생성된 벡터를 `Pinecone` 또는 `FAISS` 벡터 DB에 저장하고 인덱싱합니다.
4.  **사용자 질문 입력**: 사용자가 챗봇 인터페이스를 통해 질문을 입력합니다.
5.  **유사 문서 검색**: 사용자 질문을 벡터로 변환한 후, 벡터 DB에서 코사인 유사도가 가장 높은 문서를 검색합니다.
6.  **맞춤형 답변 생성**: 검색된 문서와 사용자 질문을 프롬프트로 구성하여 미세조정된 LLM에게 전달하고, 최종 답변을 생성하여 사용자에게 제공합니다.

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
### 설치 및 실행

1.  **프로젝트 클론**
    ```sh
    git clone https://github.com/ley38107/chatbot.git
    cd chatbot
    ```

2.  **Backend 설정**
    ```sh
    # 가상환경 생성 및 활성화
    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # macOS/Linux
    
    # 의존성 설치
    pip install -r requirements.txt
    ```

3.  **API 서버 실행**
    ```sh
    python api_server.py
    ```

4.  **API 테스트**
    ```sh
    python chat_client.py
    ```

<br>

## 📁 프로젝트 구조

```
chatbot/
├── .gitignore                    # Git 제외 파일
├── README.md                     # 프로젝트 문서
├── requirements.txt              # Python 의존성
├── api_server.py                 # FastAPI 서버
├── chat_client.py                # API 클라이언트
└── hyperclova_local_client.py    # HyperCLOVA X SEED 클라이언트
```

<br>

## 🔧 API 사용법

### 서버 실행
```bash
python api_server.py
```

### API 엔드포인트
- **POST** `/chat` - 채팅 API
- **GET** `/docs` - API 문서 (http://localhost:8000/docs)

### 요청 예시
```json
{
  "question": "안녕하세요!"
}
```

### 응답 예시
```json
{
  "answer": "안녕하세요!",
  "model_name": "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-0.5B",
  "response_time": 1.23
}
```

<br>

## 🧑‍💻 팀원 (9팀)

| 이름 | 역할 |
| :--- | :--- |
| **이희재** | PM |
| **김성수** | BE |
| **이정욱** | BE |
| **박성빈** | FE |
