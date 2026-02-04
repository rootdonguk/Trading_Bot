#!/usr/bin/env python3
"""
🔧 바이낸스 절댓값 수익 시스템 설치 및 실행 도우미

이 스크립트는 시스템 설치부터 실행까지 모든 과정을 자동화합니다.
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def install_requirements():
    """필요한 패키지 설치"""
    print("📦 필요한 패키지를 설치하는 중...")
    
    requirements = [
        'python-binance',
        'pandas',
        'numpy',
        'matplotlib',
        'requests'
    ]
    
    for package in requirements:
        try:
            print(f"   설치 중: {package}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package} 설치 완료")
        except subprocess.CalledProcessError:
            print(f"   ❌ {package} 설치 실패")
            return False
    
    print("✅ 모든 패키지 설치 완료!")
    return True

def main_menu():
    """메인 메뉴"""
    while True:
        print("\n🚀 바이낸스 절댓값 수익 시스템")
        print("="*50)
        print("1. 시스템 실행")
        print("2. 패키지 설치")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            # 시스템 실행
            try:
                import run_system
                run_system.main()
            except ImportError:
                print("❌ 시스템 파일을 찾을 수 없습니다.")
                print("필요한 파일들이 모두 있는지 확인해주세요.")
            except Exception as e:
                print(f"❌ 실행 오류: {e}")
        
        elif choice == '2':
            # 패키지 설치
            install_requirements()
        
        elif choice == '3':
            print("👋 프로그램을 종료합니다.")
            break
        
        else:
            print("❌ 올바른 선택지를 입력해주세요.")

def main():
    """메인 함수"""
    print("🚀 바이낸스 절댓값 수익 시스템 설치 및 실행 도우미")
    print("="*60)
    
    # 1. 패키지 설치 확인
    try:
        import binance
        print("✅ python-binance 패키지가 이미 설치되어 있습니다.")
    except ImportError:
        print("📦 필요한 패키지를 설치합니다...")
        if not install_requirements():
            print("❌ 패키지 설치에 실패했습니다.")
            return
    
    # 2. 메인 메뉴
    main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")