@echo off
echo 🚀 바이낸스 절댓값 수익 시스템 시작
echo ================================

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python 3.7 이상을 설치해주세요: https://python.org
    pause
    exit /b 1
)

REM 빠른 시작 실행
echo 📦 시스템을 시작합니다...
python quick_start.py

pause