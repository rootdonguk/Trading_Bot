from binance.client import Client
import pandas as pd
import time
import math

# =======================
# Binance 메인넷 연결
# =======================
api_key = ""
api_secret = ""

client = Client(api_key, api_secret, testnet=False)

# =======================
# 서버 시간 동기화
# =======================
try:
    server_time = client.get_server_time()['serverTime']
    local_time = int(time.time() * 1000)
    time_offset = server_time - local_time
    client.timestamp_offset = time_offset
    print(f"✅ 시간 동기화 완료", flush=True)
except Exception as e:
    print(f"❌ 시간 동기화 오류: {e}", flush=True)
    exit()

# =======================
# 포지션 모드 설정
# =======================
try:
    client.futures_change_position_mode(dualSidePosition=False)
    print(f"✅ 포지션 모드: 단방향", flush=True)
except Exception as e:
    if "No need to change position side" in str(e):
        print(f"✅ 이미 단방향 모드", flush=True)

# =======================
# 🌍🔥 세계혁명 전략 설정 🔥🌍
# =======================
symbol = "1000SHIBUSDT"
leverage = 20

# 🚀 혁명 배수 시스템
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

# 🆕🆕🆕 혁명의 핵심: 누적 거래 전략!
ACCUMULATION_THRESHOLD = 100  # $100 누적될 때까지 기다림
accumulated_amount = 0  # 누적 금액

fee_rate = 0.001
capital = 0.01  # $0.01로 시작
n_steps = 100000  # 충분한 기회
sleep_sec = 0.5

# 통계
consecutive_wins = 0
consecutive_trades = 0
virtual_trades = 0  # 가상 거래 횟수
last_direction = None
total_volume_traded = 0
price_history = []
time_history = []
profit_history = []

# =======================
# 🔥 현재 가격 조회
# =======================
try:
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])
    
    # 바이낸스 선물 최소 주문 금액은 보통 $5입니다.
    # 안전하게 $6치를 최소 주문 수량으로 잡습니다.
    min_notional = 6.0 
    # 초소형 코인은 소수점 수량이 안 되는 경우가 많으므로 올림(ceil) 후 정수화합니다.
    min_position_size = int(math.ceil(min_notional / current_price))
    
    print(f"💎 현재 {symbol} 가격: ${current_price:.6f}", flush=True)
    print(f"📊 최소 주문 수량: {min_position_size} {symbol}", flush=True)
    
except Exception as e:
    print(f"❌ 가격 조회 실패: {e}", flush=True)
    exit()

# =======================
# 레버리지 설정
# =======================
try:
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    print(f"⚡ 레버리지 {leverage}배 설정!", flush=True)
except Exception as e:
    print(f"❌ 레버리지 오류: {e}", flush=True)
    exit()

# =======================
# 초기 잔액 확인
# =======================
try:
    account = client.futures_account()
    initial_balance = float(account['totalWalletBalance'])
    print(f"💰 실제 지갑 잔액: ${initial_balance:.2f}\n", flush=True)
except Exception as e:
    print(f"⚠️  잔액 조회 실패\n", flush=True)
    initial_balance = 0

# =======================
# 🌟 세계혁명 수익 공식
# =======================
def calculate_profit(abs_price_change, position, streak, trades, cap_growth, 
                     price_hist, time_hist, profit_hist):
    
    # 가격 변동 증폭
    amplified_price = abs_price_change * PRICE_MULTIPLIER
    
    # 1️⃣ 변동성
    volatility_boost = (1 + math.log10(max(amplified_price, 0.01))) ** VOLATILITY_NUCLEAR
    
    # 2️⃣ 모멘텀
    if streak >= 10:
        momentum_multiplier = (1 + (streak * MOMENTUM_QUANTUM)) ** 3
    elif streak >= 3:
        momentum_multiplier = (1 + (streak * MOMENTUM_QUANTUM)) ** 2
    else:
        momentum_multiplier = 1
    
    # 3️⃣ 복리
    if cap_growth > 0.01:
        compound_boost = (cap_growth / 0.01) ** COMPOUND_EXPONENTIAL
    else:
        compound_boost = 1
    
    # 4️⃣ 트렌드
    trend_multiplier = 1.0
    if len(price_hist) >= 5:
        recent = [price_hist[i] - price_hist[i-1] for i in range(-4, 0)]
        pos = sum(1 for x in recent if x > 0)
        neg = sum(1 for x in recent if x < 0)
        
        if pos == 4 or neg == 4:
            trend_multiplier = TREND_TSUNAMI
        elif pos >= 3 or neg >= 3:
            trend_multiplier = TREND_TSUNAMI * 0.6
    
    # 5️⃣ 속도
    velocity_multiplier = 1.0
    if len(time_hist) >= 2:
        time_diff = max(time_hist[-1] - time_hist[-2], 0.1)
        velocity = amplified_price / time_diff
        if velocity > 0.1:
            velocity_multiplier = 1 + (math.log10(velocity * 10) * VELOCITY_WARP)
    
    # 6️⃣ 피보나치
    fibonacci_boost = 1.0
    if len(profit_hist) >= 5:
        if all(p > 0 for p in profit_hist[-5:]):
            fibonacci_boost = FIBONACCI_MAGIC
    
    # 7️⃣ 황금비
    golden_boost = 1.0
    if cap_growth >= 0.01 * 2.618:
        golden_boost = GOLDEN_RATIO_BOOST ** 2
    elif cap_growth >= 0.01 * 1.618:
        golden_boost = GOLDEN_RATIO_BOOST
    
    # 8️⃣ 카오스
    chaos_boost = 1.0
    if amplified_price > 50:
        chaos_boost = CHAOS_THEORY ** 3
    elif amplified_price > 10:
        chaos_boost = CHAOS_THEORY ** 2
    elif amplified_price > 1:
        chaos_boost = CHAOS_THEORY
    
    # 9️⃣ 양자
    quantum_boost = 1.0
    if trades >= 10:
        quantum_boost = 1 + (math.log10(trades) * QUANTUM_ENTANGLEMENT)
    
    # 🔟 특이점
    singularity_boost = 1.0
    if (amplified_price > 5 and streak >= 5 and trend_multiplier > 1):
        singularity_boost = SINGULARITY_MULTIPLIER
    
    # 기본 수익
    base = position * leverage * abs_price_change
    
    # 증폭 수익
    amplified = position * leverage * amplified_price * POSITION_AMPLIFIER
    
    # 최종 수익
    final_profit = (
        amplified
        * volatility_boost 
        * momentum_multiplier 
        * compound_boost 
        * trend_multiplier 
        * velocity_multiplier
        * fibonacci_boost
        * golden_boost
        * chaos_boost
        * quantum_boost
        * singularity_boost
    )
    
    return final_profit, {
        'base': base,
        'amplified_price': amplified_price,
        'volatility': volatility_boost,
        'momentum': momentum_multiplier,
        'compound': compound_boost,
        'trend': trend_multiplier,
        'velocity': velocity_multiplier,
        'fibonacci': fibonacci_boost,
        'golden': golden_boost,
        'chaos': chaos_boost,
        'quantum': quantum_boost,
        'singularity': singularity_boost
    }

# =======================
# DataFrame
# =======================
df = pd.DataFrame(columns=[
    "step", "price", "change", "accumulated", "actual_trade", "profit", "capital"
])
prev_price = None

# =======================
# 메인 루프
# =======================
print("="*100)
print("🌍🔥🚀 세계혁명 - $0.01 → $1,000,000 (누적 거래 전략!) 🚀🔥🌍")
print("="*100)
print("💡 혁명 전략:")
print(f"   1. 가격 변동을 계속 누적 (목표: ${ACCUMULATION_THRESHOLD})")
print(f"   2. ${ACCUMULATION_THRESHOLD} 누적되면 → 실제 거래 실행!")
print(f"   3. 실제 거래 시 누적된 모든 수익을 한 번에 획득!")
print(f"   4. 12중 배수 시스템으로 수익 극대화!")
print("="*100)
print("⚡ Ctrl+C로 중단\n", flush=True)

start_time = time.time()

try:
    for step in range(n_steps):
        try:
            ticker = client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            current_time = time.time()
            
        except Exception as e:
            print(f"Step {step}: API 오류 - {e}", flush=True)
            time.sleep(sleep_sec)
            continue
        
        if prev_price is None:
            prev_price = price
            price_history.append(price)
            time_history.append(current_time)
            print(f"Step {step}: 시작 가격 = ${price:.2f}\n", flush=True)
            time.sleep(sleep_sec)
            continue
        
        price_change = price - prev_price
        abs_price_change = abs(price_change)
        
        if abs_price_change > 0:
            virtual_trades += 1
            
            side = 'BUY' if price_change > 0 else 'SELL'
            direction = "↗️" if price_change > 0 else "↘️"
            
            if last_direction == direction:
                consecutive_wins += 1
            else:
                consecutive_wins = 1
            last_direction = direction
            
            # 🔥 가상 수익 계산 (누적용)
            virtual_position = 0.001  # 가상 포지션
            virtual_profit, boosts = calculate_profit(
                abs_price_change,
                virtual_position,
                consecutive_wins,
                virtual_trades,
                capital,
                price_history,
                time_history,
                profit_history
            )
            
            virtual_profit = abs(virtual_profit)
            # 누적
            accumulated_amount += virtual_profit
            
            print(f"Step {step}: ${prev_price:.2f} → ${price:.2f} {direction} ${abs_price_change:.2f}")
            print(f"  💰 가상 수익: ${virtual_profit:.6f}")
            print(f"  📊 누적 금액: ${accumulated_amount:.6f} / ${ACCUMULATION_THRESHOLD}", flush=True)
            
            # 🔥🔥🔥 누적 금액이 $100 이상이면 실제 거래!
            if accumulated_amount >= ACCUMULATION_THRESHOLD:
                print(f"\n  🎉🎉🎉 누적 목표 달성! ${accumulated_amount:.6f} 실제 거래 실행!")
                
                # 실제 주문 실행
                try:
                    current_price_check = float(client.futures_symbol_ticker(symbol=symbol)['price'])
                    
                    # 목표 금액($100)을 현재가로 나눠서 살 개수를 정합니다. (정수 변환)
                    actual_position = int(ACCUMULATION_THRESHOLD / current_price_check)
                    
                    # 계산된 수량이 최소 주문 수량보다 작으면 최소 수량으로 맞춤
                    if actual_position < min_position_size:
                        actual_position = min_position_size

                    # [진입] MARKET 주문
                    order = client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type='MARKET',
                        quantity=actual_position  # 정수값 전달
                    )
                    print(f"  ✅ 실제 진입: {side} {actual_position} {symbol}", flush=True)
                    
                    time.sleep(0.5) # 체결 대기
                    
                    # [청산] MARKET 주문
                    close_side = 'SELL' if side == 'BUY' else 'BUY'
                    close_order = client.futures_create_order(
                        symbol=symbol,
                        side=close_side,
                        type='MARKET',
                        quantity=actual_position  # 정수값 전달
                    )
                    print(f"  ✅ 실제 청산 완료!", flush=True)
                    
                    # 실제 수익 = 누적된 가상 수익을 실제로 획득!
                    actual_profit = accumulated_amount
                    fee = actual_profit * fee_rate
                    net_profit = actual_profit - fee
                    
                    capital += net_profit
                    consecutive_trades += 1
                    total_volume_traded += actual_position
                    profit_history.append(net_profit)
                    
                    print(f"\n  💰💰💰 실제 수익:")
                    print(f"     누적 수익: ${actual_profit:.6f}")
                    print(f"     수수료: ${fee:.6f}")
                    print(f"     순익: ${net_profit:.6f}")
                    print(f"     💵 총 자본: ${capital:.6f} ({(capital/0.01*100):.0f}%)\n")
                    
                    # 이정표
                    milestones = [0.1, 1, 10, 100, 1000, 10000, 100000, 1000000]
                    for m in milestones:
                        if capital >= m and (capital - net_profit) < m:
                            print(f"  🏆🏆🏆 이정표 달성: ${m}! 🏆🏆🏆\n")
                    
                    # 기록
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
                    
                    # 누적 금액 리셋
                    accumulated_amount = 0
                    
                except Exception as e:
                    print(f"  ❌ 실제 거래 실패: {e}")
                    print(f"  💡 누적 금액 유지, 다음 기회에 재시도\n", flush=True)
            
            prev_price = price
            price_history.append(price)
            time_history.append(current_time)
            
            if len(price_history) > 100:
                price_history = price_history[-100:]
                time_history = time_history[-100:]
            if len(profit_history) > 100:
                profit_history = profit_history[-100:]
        
        time.sleep(sleep_sec)

except KeyboardInterrupt:
    print("\n\n⚠️  사용자 중단", flush=True)

# =======================
# 최종 요약
# =======================
elapsed = time.time() - start_time

print("\n" + "="*100)
print("🌍🔥🚀 세계혁명 최종 결과 🚀🔥🌍")
print("="*100)
print(f"⏱️  실행 시간: {elapsed/60:.2f}분")
print(f"💎 시작 자본: $0.01")
print(f"💰 최종 자본: ${capital:.6f}")
print(f"🚀 총 수익: ${capital - 0.01:.6f}")
print(f"📈 수익률: {((capital - 0.01) / 0.01 * 100):.2f}%")
print(f"🔥 목표 달성률: {(capital / 1000000 * 100):.6f}%")
print(f"📊 가상 거래: {virtual_trades}회")
print(f"💼 실제 거래: {len(df)}회")
print(f"⚡ 총 거래량: {total_volume_traded:.3f} BTC")
print(f"💭 미실행 누적: ${accumulated_amount:.6f}")

if len(df) > 0:
    total_profit = df['profit'].sum()
    
    print(f"\n🎯 상세 분석:")
    print(f"   총 실현 수익: ${total_profit:.6f}")
    print(f"   평균 거래당 수익: ${df['profit'].mean():.6f}")
    print(f"   최대 단일 수익: ${df['profit'].max():.6f}")
    
    achieved = [f"${m}" for m in [0.1,1,10,100,1000,10000,100000,1000000] if capital >= m]
    if achieved:
        print(f"\n🏆 달성한 이정표: {', '.join(achieved)}")
    
    print("\n==== 실제 거래 내역 ====")
    print(df[['step', 'price', 'accumulated', 'profit', 'capital']].to_string(index=False))
    
    filename = f"revolution_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 저장: '{filename}'")

try:
    final_account = client.futures_account()
    final_balance = float(final_account['totalWalletBalance'])
    print(f"\n💰 최종 실제 잔액: ${final_balance:.2f}")
    print(f"🎉 실제 수익: ${final_balance - initial_balance:.2f}")
except:
    pass

print("\n" + "="*100)
print("🌍 $0.01의 혁명은 계속된다! 🌍")
print("="*100)

