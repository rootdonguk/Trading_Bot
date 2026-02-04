#!/bin/bash

echo "🚀 바이낸스 절댓값 수익 시스템 시작"
echo "================================"

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되지 않았습니다."
    echo "Python 3.7 이상을 설치해주세요."
    exit 1
fi

# 실행 권한 부여
chmod +x quick_start.py
chmod +x run_system.py

# 빠른 시작 실행
echo "📦 시스템을 시작합니다..."
python3 quick_start.py