@echo off
REM Docker 백그라운드 실행 스크립트

echo ===============================
echo 챗봇 Docker 백그라운드 실행
echo ===============================

docker-compose up -d --build

echo.
echo [OK] 서버가 백그라운드에서 실행 중입니다.
echo.
echo 접속 주소:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:5000
echo   API 문서: http://localhost:5000/docs
echo.
echo 로그 확인: docker-compose logs -f
echo 종료하기:   docker-compose down
echo.

