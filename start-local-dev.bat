@echo off
chcp 65001 > nul
echo ================================================
echo 로컬 개발 환경 시작
echo ================================================
echo.

REM 프로젝트 루트 디렉토리 확인
cd /d %~dp0

REM .env 파일 확인
if not exist .env (
    echo [경고] .env 파일이 없습니다.
    echo.
    choice /C YN /M "setup-local-env.bat를 실행하시겠습니까? (Y/N)"
    if errorlevel 2 (
        echo.
        echo [취소] .env 파일을 먼저 생성해주세요.
        pause
        exit /b
    )
    echo.
    call setup-local-env.bat
)

REM 백엔드 폴더 확인
if not exist backend (
    echo [오류] backend 폴더를 찾을 수 없습니다.
    pause
    exit /b 1
)

REM 프론트엔드 폴더 확인
if not exist frontend (
    echo [오류] frontend 폴더를 찾을 수 없습니다.
    pause
    exit /b 1
)

echo [시작] 백엔드와 프론트엔드를 실행합니다...
echo.

REM 백엔드 실행 (새 터미널 창)
echo [1/2] 백엔드 서버 시작 중...
start "Chatbot Backend" cmd /k "cd /d %~dp0backend && (if not exist venv (echo [백엔드] 가상환경 생성 중... && python -m venv venv)) && echo [백엔드] 가상환경 활성화 중... && call venv\Scripts\activate.bat && echo [백엔드] 패키지 설치 중... && python -m pip install --upgrade pip > nul 2>&1 && pip install -r requirements.txt && echo [백엔드] 서버 시작 중... && python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload || echo [백엔드 오류] 서버 시작에 실패했습니다. && pause"

REM 백엔드가 시작될 때까지 잠시 대기
timeout /t 5 /nobreak > nul

REM 프론트엔드 실행 (새 터미널 창)
echo [2/2] 프론트엔드 서버 시작 중...
start "Chatbot Frontend" cmd /k "cd /d %~dp0frontend && (if not exist node_modules (echo [프론트엔드] 패키지 설치 중... && npm install)) && echo [프론트엔드] 서버 시작 중... && npm start || echo [프론트엔드 오류] 서버 시작에 실패했습니다. && pause"

echo.
echo ================================================
echo [완료] 백엔드와 프론트엔드가 실행되었습니다!
echo ================================================
echo.
echo 백엔드: http://localhost:5000
echo 백엔드 API 문서: http://localhost:5000/docs
echo 프론트엔드: http://localhost:3000
echo.
echo 서버를 종료하려면 각 터미널 창에서 Ctrl+C를 누르세요.
echo.
pause

