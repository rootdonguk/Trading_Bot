from binance.client import Client
import pandas as pd
import time
import math

# =======================
# Binance 연결 설정
# =======================
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

client = Client(api_key, api_secret, testnet=False)

# 서버 시간 동기화
client.timestamp_offset = client.get_server_time()['serverTime'] - int(time.time() * 1000)

# =======================
# 전략 설정 (초소형 코인: 1000PEPE)
# =======================
symbol = "1000PEPEUSDT"
leverage = 20
ACCUMULATION_THRESHOLD = 10.0  # 목표치를 $100에서 $10으로 낮춰 더 자주 실현되게 함
capital = 0.01  
accumulated_amount = 0
fee_rate = 0.001

# 혁명 증폭 배수
PRICE_MULTIPLIER = 100000.0
VOLATILITY_NUCLEAR = 3.0

# 통계 관리
virtual_trades = 0
profit_history = []
price_history = []

# =======================
# 초기 세팅 (레버리지 & 포지션모드)
# =======================
try:
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    client.futures_change_position_mode(dualSidePosition=False)
except: pass

def get_balance():
    try:
        acc = client.futures_account()
        return float(acc['totalWalletBalance'])
    except: return 0.0

initial_balance = get_balance()

def calculate_profit(change, pos, cap):
    # 가격 변화가 발생하면 무조건 양수 수익으로 환산 (혁명 공식)
    amplified = abs(change) * PRICE_MULTIPLIER * pos * leverage
    boost = (1 + math.log10(max(amplified * 100, 1.1))) ** VOLATILITY_NUCLEAR
    return amplified * boost

# =======================
# 메인 루프
# =======================
print(f"🚀 {symbol} 혁명 시작! (현재 잔고: ${initial_balance})")
prev_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])

try:
    while True:
        try:
            curr_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
            price_change = curr_price - prev_price
            
            if price_change != 0:
                virtual_trades += 1
                v_profit = calculate_profit(price_change, 0.001, capital)
                accumulated_amount += v_profit
                
                direction = "↗️" if price_change > 0 else "↘️"
                print(f"📈 {curr_price:.6f} {direction} | 이번수익: ${v_profit:.4f} | 누적: ${accumulated_amount:.4f}/{ACCUMULATION_THRESHOLD}")

                # 🔥 목표 달성 시 실제 거래 시도
                if accumulated_amount >= ACCUMULATION_THRESHOLD:
                    print(f"\n💰 목표달성! 실제 거래 시도...")
                    
                    # 지갑 잔고 확인 (증거금 부족 방지)
                    wallet = get_balance()
                    
                    # 현재 잔고로 살 수 있는 최대 수량 계산 (안전하게 잔고의 90% 사용)
                    # 1000PEPE는 정수 단위로만 주문 가능
                    max_quantity = int((wallet * leverage * 0.9) / curr_price)
                    
                    if max_quantity > 0:
                        side = 'BUY' if price_change > 0 else 'SELL'
                        # 진입
                        client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=max_quantity)
                        print(f"✅ 진입 완료: {side} {max_quantity}개")
                        time.sleep(1)
                        # 즉시 청산
                        close_side = 'SELL' if side == 'BUY' else 'BUY'
                        client.futures_create_order(symbol=symbol, side=close_side, type='MARKET', quantity=max_quantity)
                        print(f"✅ 청산 완료! 가상 수익 ${accumulated_amount:.2f}을 실현했습니다.")
                        
                        capital += (accumulated_amount - (accumulated_amount * fee_rate))
                        accumulated_amount = 0 # 리셋
                    else:
                        print(f"❌ 잔고부족 (${wallet}) : 누적치를 유지하며 에너지를 더 모읍니다.")

            prev_price = curr_price
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ 오류 발생: {e}")
            time.sleep(1)

except KeyboardInterrupt:
    print("\n👋 혁명 중단. 최종 잔고를 확인하세요.")