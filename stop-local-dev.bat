@echo off
chcp 65001 > nul
echo ================================================
echo 로컬 개발 환경 종료
echo ================================================
echo.

echo [종료] 실행 중인 백엔드/프론트엔드 프로세스를 찾는 중...
echo.

REM 포트 5000 (백엔드) 사용 중인 프로세스 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo [백엔드] 프로세스 종료 중 (PID: %%a)
    taskkill /F /PID %%a > nul 2>&1
)

REM 포트 3000 (프론트엔드) 사용 중인 프로세스 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo [프론트엔드] 프로세스 종료 중 (PID: %%a)
    taskkill /F /PID %%a > nul 2>&1
)

echo.
echo ================================================
echo [완료] 개발 서버가 종료되었습니다.
echo ================================================
echo.
pause

