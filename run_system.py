#!/usr/bin/env python3
"""
🚀 바이낸스 절댓값 수익 시스템 실행 스크립트

사용법:
python run_system.py
"""

import sys
import time

def get_system_choice():
    """시스템 선택"""
    print("🚀 바이낸스 절댓값 수익 보장 시스템")
    print("="*50)
    
    print("\n🔧 시스템을 선택하세요:")
    print("1. 기본 시스템 (단일 코인, 간단한 구조)")
    print("2. 고급 시스템 (다중 코인, 복리 최적화)")
    
    while True:
        choice = input("\n선택 (1 또는 2, 기본값: 2): ").strip()
        if choice == '1':
            return 'basic'
        elif choice in ['2', '']:
            return 'advanced'
        else:
            print("❌ 1 또는 2를 입력해주세요.")

def main():
    """메인 함수"""
    try:
        # 시스템 선택
        system_type = get_system_choice()
        
        if system_type == 'basic':
            # 기본 시스템 실행
            from absolute_profit_system import main as run_basic_system
            run_basic_system()
        else:
            # 고급 시스템 실행
            from advanced_compound_system import main as run_advanced_system
            run_advanced_system()
        
    except KeyboardInterrupt:
        print("\n⚠️  사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()