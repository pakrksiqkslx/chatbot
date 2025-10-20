# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "로컬 개발 환경 설정 스크립트" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# .env 파일이 이미 있는지 확인
if (Test-Path .env) {
    Write-Host "[경고] .env 파일이 이미 존재합니다." -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "기존 .env 파일을 덮어쓰시겠습니까? (Y/N)"
    if ($response -ne 'Y' -and $response -ne 'y') {
        Write-Host ""
        Write-Host "[취소] .env 파일을 유지합니다." -ForegroundColor Yellow
        pause
        exit
    }
    Write-Host ""
    Write-Host "[삭제] 기존 .env 파일을 삭제합니다..." -ForegroundColor Yellow
    Remove-Item .env
}

Write-Host "[생성] .env 파일을 생성합니다..." -ForegroundColor Green
Write-Host ""

# .env 파일 내용
$envContent = @"
# HyperCLOVA X API 설정
HYPERCLOVA_API_KEY=nv-93ec8a8d596946b2b2314d70dcdba676qLCw

# PINECONE 설정
PINECONE_API_KEY=pcsk_2gNHZ_ChuVt8WRLZwrFuvV8jH1LLAaqNJgSGTreVyFmN5B6p2GVxznjLaySDQKD38nXcv
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=chatbot-courses

# 벡터 스토어 설정
USE_PINECONE=true

# 서버 설정
PORT=5000
HOST=0.0.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
"@

# UTF-8 without BOM으로 저장
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$PWD\.env", $envContent, $utf8NoBom)

Write-Host "================================================" -ForegroundColor Green
Write-Host "[완료] .env 파일이 생성되었습니다!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "이제 로컬에서 개발할 수 있습니다:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. 백엔드 실행:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     python -m venv venv" -ForegroundColor Gray
Write-Host "     venv\Scripts\activate" -ForegroundColor Gray
Write-Host "     pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "     uvicorn main:app --host 0.0.0.0 --port 5000 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 프론트엔드 실행:" -ForegroundColor White
Write-Host "     cd frontend" -ForegroundColor Gray
Write-Host "     npm install" -ForegroundColor Gray
Write-Host "     npm start" -ForegroundColor Gray
Write-Host ""

pause

