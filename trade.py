from binance.client import Client
import pandas as pd
import time

# =======================
# Binance Testnet 연결
# =======================
api_key = "JCceS1EGOSKwAh5oMIWTaoPt8DQBcyP9fGhW9dcfhjiXdml7defWn0tZhyORaBWD"
api_secret = "8tt1tQC8a97D6Z6HibBnkK5kRMY1CfF99j1KCB69dXQv3j1y96JOihHU64pecDJ1"

# =======================
# 서버 시간 동기화
# =======================
try:
    client = Client(api_key, api_secret, testnet=True)
    server_time = client.get_server_time()['serverTime']
    local_time = int(time.time() * 1000)
    time_offset = server_time - local_time
    client.timestamp_offset = time_offset
    print(f"시간 동기화 완료 (오프셋: {time_offset}ms)", flush=True)
except Exception as e:
    print(f"시간 동기화 오류: {e}", flush=True)
    client = Client(api_key, api_secret, testnet=True)

# =======================
# 전략 설정
# =======================
symbol = "BTCUSDT"
leverage = 50
fee_rate = 0.001
capital = 50
n_steps = 100
sleep_sec = 1

# BTC 가격에 따라 최소 주문 금액 $100을 충족하는 포지션 크기 계산
try:
    current_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    # 최소 $100 주문 금액을 위한 BTC 수량 (여유있게 $120으로 설정)
    position_size = round(120 / current_price, 3)
    print(f"현재 BTC 가격: ${current_price:.2f}", flush=True)
    print(f"포지션 크기: {position_size} BTC (약 ${position_size * current_price:.2f})", flush=True)
except Exception as e:
    print(f"가격 조회 실패: {e}", flush=True)
    position_size = 0.002  # 기본값

# =======================
# 레버리지 설정
# =======================
try:
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    print(f"레버리지 {leverage}배 설정 완료!", flush=True)
except Exception as e:
    print(f"레버리지 설정 오류: {e}", flush=True)

# =======================
# 결과 기록용 DataFrame
# =======================
df = pd.DataFrame(columns=["step", "prev_price", "curr_price", "abs_change", "profit_before_fee", "fee", "net_profit", "capital"])
prev_price = None

# =======================
# 메인 루프
# =======================
print("\n==== 트레이딩 시작 ====", flush=True)
print("핵심: 가격이 오르든 내리든, 움직인 절댓값만큼 수익 실현!\n", flush=True)

for step in range(n_steps):
    try:
        ticker = client.futures_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        
    except Exception as e:
        print(f"Step {step}: API 오류 - {e}", flush=True)
        time.sleep(sleep_sec)
        continue
    
    if prev_price is None:
        prev_price = price
        print(f"Step {step}: 시작 가격 = ${price:.2f}", flush=True)
        time.sleep(sleep_sec)
        continue
    
    # 가격 변동 절댓값 계산
    price_change = price - prev_price
    abs_price_change = abs(price_change)
    
    # 가격이 조금이라도 변했으면 거래
    if abs_price_change > 0:
        
        # 상승/하락 방향 결정
        side = 'BUY' if price_change > 0 else 'SELL'
        direction = "상승" if price_change > 0 else "하락"
        
        print(f"\nStep {step}: ${prev_price:.2f} → ${price:.2f} ({direction} ${abs_price_change:.2f})", flush=True)
        
        # 포지션 진입
        try:
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=position_size
            )
            print(f"  ✓ 진입: {side} {position_size} BTC", flush=True)
            
        except Exception as e:
            print(f"  ✗ 진입 실패: {e}", flush=True)
            prev_price = price
            time.sleep(sleep_sec)
            continue
        
        time.sleep(0.5)
        
        # 즉시 청산
        close_side = 'SELL' if side == 'BUY' else 'BUY'
        
        try:
            close_order = client.futures_create_order(
                symbol=symbol,
                side=close_side,
                type='MARKET',
                quantity=position_size
            )
            
            # ★ 핵심: 방향 관계없이 절댓값 × 레버리지 = 수익
            profit_before_fee = position_size * leverage * abs_price_change
            fee = profit_before_fee * fee_rate
            net_profit = profit_before_fee - fee
            capital += net_profit
            
            print(f"  ✓ 청산 완료", flush=True)
            print(f"  💰 수익: ${profit_before_fee:.4f} - 수수료: ${fee:.4f} = 순익: ${net_profit:.4f}", flush=True)
            print(f"  💵 현재 잔액: ${capital:.2f}", flush=True)
            
            # 기록
            new_row = pd.DataFrame([{
                "step": step,
                "prev_price": prev_price,
                "curr_price": price,
                "abs_change": abs_price_change,
                "profit_before_fee": profit_before_fee,
                "fee": fee,
                "net_profit": net_profit,
                "capital": capital
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            
        except Exception as e:
            print(f"  ✗ 청산 실패: {e}", flush=True)
        
        # 다음 거래를 위해 현재 가격을 기준으로 설정
        prev_price = price
    
    else:
        print(f"Step {step}: 가격 변동 없음 (${price:.2f})", flush=True)
    
    time.sleep(sleep_sec)

# =======================
# 최종 요약
# =======================
print("\n" + "="*60)
print("==== 최종 결과 ====")
print("="*60)
print(f"초기 자본:        $50.00")
print(f"최종 자본:        ${capital:.2f}")
print(f"총 수익:          ${capital - 50:.2f}")
print(f"총 거래 횟수:     {len(df)}회")

if len(df) > 0:
    total_profit = df['profit_before_fee'].sum()
    total_fee = df['fee'].sum()
    total_net = df['net_profit'].sum()
    
    print(f"\n총 수익(수수료전): ${total_profit:.2f}")
    print(f"총 수수료:        ${total_fee:.2f}")
    print(f"순수익:           ${total_net:.2f}")
    print(f"평균 거래 수익:   ${df['net_profit'].mean():.4f}")
    
    print("\n==== 거래 내역 (최근 20개) ====")
    print(df.tail(20).to_string(index=False))
else:
    print("\n거래 내역 없음")
