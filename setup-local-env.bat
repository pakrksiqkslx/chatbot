@echo off
chcp 65001 > nul
echo ================================================
echo 로컬 개발 환경 설정 스크립트
echo ================================================
echo.

REM .env 파일이 이미 있는지 확인
if exist .env (
    echo [경고] .env 파일이 이미 존재합니다.
    echo.
    choice /C YN /M "기존 .env 파일을 덮어쓰시겠습니까? (Y/N)"
    if errorlevel 2 (
        echo.
        echo [취소] .env 파일을 유지합니다.
        goto :end
    )
    echo.
    echo [삭제] 기존 .env 파일을 삭제합니다...
    del .env
)

echo [생성] .env 파일을 생성합니다...
echo.

REM .env 파일 생성
(
echo # HyperCLOVA X API 설정 - 실제 API 키로 교체하세요
echo HYPERCLOVA_API_KEY=your-hyperclova-api-key-here
echo.
echo # PINECONE 설정 - 실제 API 키로 교체하세요
echo PINECONE_API_KEY=your-pinecone-api-key-here
echo PINECONE_INDEX_NAME=chatbot-courses
echo.
echo # 서버 설정
echo PORT=5000
echo HOST=0.0.0.0
echo ENVIRONMENT=development
echo DEBUG=true
echo LOG_LEVEL=INFO
) > .env

echo ================================================
echo [완료] .env 파일이 생성되었습니다!
echo ================================================
echo.
echo ⚠️  중요: .env 파일의 API 키를 실제 키로 교체하세요!
echo.
echo API 키 발급 방법:
echo   - HyperCLOVA X: https://clovastudio.ncloud.com/
echo   - PINECONE: https://www.pinecone.io/
echo.
echo 이제 로컬에서 개발할 수 있습니다:
echo.
echo   1. 백엔드 실행:
echo      cd backend
echo      python -m venv venv
echo      venv\Scripts\activate
echo      pip install -r requirements.txt
echo      uvicorn main:app --host 0.0.0.0 --port 5000 --reload
echo.
echo   2. 프론트엔드 실행:
echo      cd frontend
echo      npm install
echo      npm start
echo.

:end
pause

