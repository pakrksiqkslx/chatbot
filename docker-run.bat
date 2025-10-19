@echo off
REM Docker로 챗봇 실행 스크립트

echo ===============================
echo 수업계획서 챗봇 Docker 실행
echo ===============================

REM 벡터스토어 존재 확인
if not exist "vectorstore\faiss_index\index.faiss" (
    echo.
    echo [경고] 벡터스토어가 없습니다!
    echo 먼저 다음 명령어를 실행하세요:
    echo   python vectorize_courses.py
    echo.
    pause
    exit /b 1
)

echo.
echo [1] 벡터스토어 확인 완료
echo [2] Docker 컨테이너 빌드 및 실행 중...
echo.

docker-compose up --build

echo.
echo ===============================
echo 종료되었습니다.
echo ===============================

