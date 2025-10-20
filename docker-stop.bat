@echo off
REM Docker 중지 스크립트

echo ===============================
echo 챗봇 Docker 중지
echo ===============================

docker-compose down

echo.
echo [OK] 모든 컨테이너가 중지되었습니다.
echo.

