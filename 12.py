from binance.client import Client
import pandas as pd
import time
import math
import sys

# =============================================
# 1. API 연결 & 시간 동기화
# =============================================
api_key = "jpiscnUedm1PehgyBryWBsee5NEkxaupeB39htBK9SIdBBqLxsn6aVvfzxNErTV3"
api_secret = "p70gLegDXsBlNHhrK8abUgxdG17XDM8arIvFmfbn3oLlNif5C4IqHZPapm5PAakm"

# 수정: recvWindow 제거, timeout만 사용
client = Client(
    api_key,
    api_secret,
    testnet=False,
    requests_params={"timeout": 10}
)

# calculate_profit 함수 정의
def calculate_profit(price_change, position, consecutive_wins, virtual_trades, capital, price_history, time_history, profit_history):
    leverage = 20
    base_profit = price_change * position * leverage
    if len(profit_history) > 0 and profit_history[-1] > 0:
        base_profit *= (1 + (consecutive_wins * 0.1))
    return base_profit, 0

# 서버 시간 동기화 (recvWindow 대신 정확한 시간 동기화로 해결)
try:
    server_time = client.get_server_time()['serverTime']
    local_time = int(time.time() * 1000)
    time_offset = server_time - local_time
    client.timestamp_offset = time_offset
    print(f"✅ 서버 시간 동기화 완료 (오차 {time_offset}ms)", flush=True)
    
    # 시간 오차가 큰 경우 경고
    if abs(time_offset) > 5000:  # 5초 이상 차이나면
        print(f"⚠️  시간 오차가 큽니다: {time_offset}ms")
        print("   시스템 시간을 동기화하세요: w32tm /resync (Windows)")
except Exception as e:
    print(f"❌ 시간 동기화 실패: {e}", flush=True)
    sys.exit(1)

# =============================================
# 2. 포지션 모드 & 레버리지 설정
# =============================================
try:
    client.futures_change_position_mode(dualSidePosition=False)
    print("✅ 포지션 모드: 단방향")
except Exception as e:
    if "No need to change position side" in str(e):
        print("✅ 이미 단방향 모드")

try:
    client.futures_change_leverage(symbol="BTCUSDT", leverage=20)
    print("⚡ 레버리지 20배 설정 완료")
except Exception as e:
    print(f"레버리지 설정 실패 (무시 가능): {e}")

# =============================================
# 3. 세계혁명 전략 설정
# =============================================
symbol = "BTCUSDT"
ACCUMULATION_THRESHOLD = 100.0  # $100 누적 시 실제 거래
capital = 0.01                  # 시작 자본 $0.01
fee_rate = 0.001                # taker fee 가정
sleep_sec = 0.5

# 혁명 배수 상수
VOLATILITY_NUCLEAR = 3.0
MOMENTUM_QUANTUM = 0.5
COMPOUND_EXPONENTIAL = 2.0
TREND_TSUNAMI = 5.0
VELOCITY_WARP = 10.0
FIBONACCI_MAGIC = 1.618
GOLDEN_RATIO_BOOST = 2.618
CHAOS_THEORY = 3.14159
QUANTUM_ENTANGLEMENT = 7.0
SINGULARITY_MULTIPLIER = 100.0
POSITION_AMPLIFIER = 1000.0
PRICE_MULTIPLIER = 10000.0

accumulated_amount = 0.0
virtual_trades = 0
consecutive_wins = 0
last_direction = None
total_volume_traded = 0.0
price_history = []
time_history = []
profit_history = []
df = pd.DataFrame(columns=["step", "price", "change", "accumulated", "actual_trade", "profit", "capital"])

prev_price = None
step = 0
start_time = time.time()

print("="*80)
print("🌍 세계혁명 전략 시작 - $0.01 → 무한 복리")
print(f"심볼: {symbol} | 누적 목표: ${ACCUMULATION_THRESHOLD}")
print("="*80)

try:
    while True:
        step += 1
        try:
            price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
            current_time = time.time()
        except Exception as e:
            print(f"Step {step}: API 오류 - {e}")
            time.sleep(sleep_sec)
            continue

        if prev_price is None:
            prev_price = price
            price_history.append(price)
            time_history.append(current_time)
            print(f"Step {step}: 기준 가격 설정 = ${price:.2f}")
            time.sleep(sleep_sec)
            continue

        price_change = price - prev_price
        abs_price_change = abs(price_change)

        if abs_price_change > 0:
            virtual_trades += 1

            direction = "↗️" if price_change > 0 else "↘️"
            if last_direction == direction:
                consecutive_wins += 1
            else:
                consecutive_wins = 1
            last_direction = direction

            virtual_position = 0.001
            virtual_profit, _ = calculate_profit(
                abs_price_change,
                virtual_position,
                consecutive_wins,
                virtual_trades,
                capital,
                price_history,
                time_history,
                profit_history
            )

            accumulated_amount += virtual_profit

            print(f"Step {step}: ${prev_price:.2f} → ${price:.2f} {direction} ${abs_price_change:.6f}")
            print(f"   가상 수익: ${virtual_profit:.6f} | 누적: ${accumulated_amount:.6f}")

            if accumulated_amount >= ACCUMULATION_THRESHOLD:
                print(f"\n🎯 누적 목표 달성! 실제 거래 실행!")

                try:
                    current_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
                    actual_position = round(ACCUMULATION_THRESHOLD / current_price, 3)

                    order = client.futures_create_order(
                        symbol=symbol,
                        side='BUY' if price_change > 0 else 'SELL',
                        type='MARKET',
                        quantity=actual_position
                    )
                    print(f"실제 진입: {'BUY' if price_change > 0 else 'SELL'} {actual_position}")

                    time.sleep(0.5)

                    close_side = 'SELL' if price_change > 0 else 'BUY'
                    client.futures_create_order(
                        symbol=symbol,
                        side=close_side,
                        type='MARKET',
                        quantity=actual_position,
                        reduceOnly=True
                    )
                    print("실제 청산 완료!")

                    actual_profit = accumulated_amount
                    fee = actual_profit * fee_rate
                    net_profit = actual_profit - fee

                    capital += net_profit
                    total_volume_traded += actual_position
                    profit_history.append(net_profit)

                    print(f"실제 순익: ${net_profit:.6f} (수수료 ${fee:.6f})")
                    print(f"현재 자본: ${capital:.6f}\n")

                    new_row = pd.DataFrame([{
                        "step": step,
                        "price": price,
                        "change": abs_price_change,
                        "accumulated": accumulated_amount,
                        "actual_trade": "YES",
                        "profit": net_profit,
                        "capital": capital
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)

                    accumulated_amount = 0.0

                except Exception as e:
                    print(f"실제 거래 실패: {e}")
                    print("누적 유지 → 다음 기회 대기\n")

        prev_price = price
        price_history.append(price)
        time_history.append(current_time)

        if len(price_history) > 200:
            price_history = price_history[-200:]
            time_history = time_history[-200:]

        time.sleep(sleep_sec)

except KeyboardInterrupt:
    print("\n사용자 중단 (Ctrl+C)")

# 최종 요약
elapsed = time.time() - start_time
print("\n" + "="*80)
print("세계혁명 최종 결과")
print("="*80)
print(f"총 실행 시간: {elapsed/60:.2f} 분")
print(f"시작 자본: $0.01")
print(f"최종 자본: ${capital:.6f}")
print(f"총 수익: ${capital - 0.01:.6f} ({((capital - 0.01)/0.01 * 100):.2f}%)")
print(f"가상 거래: {virtual_trades} 회")
print(f"실제 거래: {len(df)} 회")
print(f"총 거래량: {total_volume_traded:.3f} BTC")
print(f"남은 누적: ${accumulated_amount:.6f}")

if len(df) > 0:
    print("\n실제 거래 내역")
    print(df.to_string(index=False))
    filename = f"revolution_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"\n결과 저장: {filename}")

print("\n세계혁명은 계속된다...")
