#!/usr/bin/env python3
"""
🚀 바이낸스 절댓값 수익 시스템 - 빠른 시작

이 스크립트는 처음 실행 시 모든 설정을 입력받아 바로 거래를 시작합니다.
"""

import subprocess
import sys
import os

def install_packages():
    """필요한 패키지 설치"""
    print("📦 필요한 패키지를 확인하는 중...")
    
    packages = ['python-binance', 'pandas', 'numpy']
    missing_packages = []
    
    for package in packages:
        try:
            if package == 'python-binance':
                import binance
            elif package == 'pandas':
                import pandas
            elif package == 'numpy':
                import numpy
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 설치 중: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 설치 완료")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 설치 실패")
                return False
    else:
        print("✅ 모든 패키지가 이미 설치되어 있습니다.")
    
    return True

def main():
    """메인 함수"""
    print("🚀 바이낸스 절댓값 수익 시스템 - 빠른 시작")
    print("="*60)
    
    # 패키지 설치 확인
    if not install_packages():
        print("❌ 패키지 설치에 실패했습니다.")
        input("Enter를 눌러 종료...")
        return
    
    print("\n🎯 시스템을 시작합니다...")
    print("모든 설정은 실행 중에 입력받습니다.")
    
    try:
        # run_system.py 실행
        import run_system
        run_system.main()
    except ImportError:
        print("❌ 시스템 파일을 찾을 수 없습니다.")
        print("run_system.py 파일이 같은 폴더에 있는지 확인해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    input("\nEnter를 눌러 종료...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        input("Enter를 눌러 종료...")