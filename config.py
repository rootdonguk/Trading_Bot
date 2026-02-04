"""
🔧 바이낸스 절댓값 수익 시스템 설정 파일
"""

# =======================
# 바이낸스 API 설정
# =======================
# ⚠️ 실제 API 키로 교체하세요!
BINANCE_CONFIG = {
    # 테스트넷 설정 (안전한 테스트용)
    'testnet': {
        'api_key': 'YOUR_TESTNET_API_KEY',
        'api_secret': 'YOUR_TESTNET_API_SECRET',
        'testnet': True
    },
    
    # 메인넷 설정 (실제 거래용)
    'mainnet': {
        'api_key': 'YOUR_MAINNET_API_KEY',
        'api_secret': 'YOUR_MAINNET_API_SECRET',
        'testnet': False
    }
}

# =======================
# 거래 전략 설정
# =======================
TRADING_CONFIG = {
    # 기본 설정
    'symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'],
    'base_leverage': 20,
    'max_leverage': 125,
    'initial_capital': 1000.0,  # 초기 자본 ($)
    
    # 복리 설정
    'reinvest_strategies': {
        'conservative': 0.5,  # 50% 재투자
        'moderate': 0.7,      # 70% 재투자  
        'aggressive': 0.9     # 90% 재투자
    },
    'default_strategy': 'moderate',
    
    # 수익 목표
    'profit_targets': {
        'hourly': 0.05,   # 시간당 5%
        'daily': 0.1,     # 일일 10%
        'weekly': 0.5,    # 주간 50%
        'monthly': 2.0    # 월간 200%
    },
    
    # 리스크 관리
    'max_daily_loss_ratio': 0.05,  # 일일 최대 손실 5%
    'stop_loss_threshold': 0.02,   # 2% 손실 시 중단
    'min_price_change': 0.01,      # 최소 가격 변동 ($0.01)
    
    # 거래 설정
    'trade_interval': 0.5,          # 거래 간격 (초)
    'max_position_ratio': 0.3,     # 최대 포지션 비율 (자본의 30%)
    'min_position_value': 100,     # 최소 포지션 가치 ($100)
    
    # 수수료
    'fee_rate': 0.001  # 0.1%
}

# =======================
# 시스템 설정
# =======================
SYSTEM_CONFIG = {
    # 로깅
    'log_level': 'INFO',
    'log_file': 'trading.log',
    'save_trades': True,
    
    # 멀티스레딩
    'max_workers': 5,
    'enable_multi_symbol': True,
    
    # 모니터링
    'status_update_interval': 60,  # 상태 업데이트 간격 (초)
    'auto_save_interval': 300,     # 자동 저장 간격 (초)
    
    # 안전 설정
    'enable_emergency_stop': True,
    'max_consecutive_losses': 5,
    'circuit_breaker_loss': 0.1   # 10% 손실 시 자동 중단
}

# =======================
# 알림 설정 (선택사항)
# =======================
NOTIFICATION_CONFIG = {
    'enable_notifications': False,
    
    # 텔레그램 봇 (선택사항)
    'telegram': {
        'bot_token': 'YOUR_TELEGRAM_BOT_TOKEN',
        'chat_id': 'YOUR_CHAT_ID'
    },
    
    # 이메일 (선택사항)
    'email': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
}

# =======================
# 백테스팅 설정
# =======================
BACKTEST_CONFIG = {
    'enable_backtest': False,
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'initial_balance': 1000.0,
    'data_source': 'binance'  # 'binance' or 'csv'
}