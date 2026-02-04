from binance.client import Client
import time
import pandas as pd

# =======================
# Binance Testnet 연결
# =======================
api_key = "JCceS1EGOSKwAh5oMIWTaoPt8DQBcyP9fGhW9dcfhjiXdml7defWn0tZhyORaBWD"
api_secret = "8tt1tQC8a97D6Z6HibBnkK5kRMY1CfF99j1KCB69dXQv3j1y96JOihHU64pecDJ1"

client = Client(api_key, api_secret, testnet=True)

symbol = "BTCUSDT"
leverage = 50
fee_rate = 0.001  # 수수료

# =======================
# 초기 설정
# =======================
capital = 50  # 초기 자본
position_size = 0.001  # BTC 단위 (테스트용 소량)
profit_threshold = 50  # $50 가격 변동마다 수익 실현
n_steps = 10  # Demo 테스트 단계
sleep_sec = 1

# 레버리지 설정
client.futures_change_leverage(symbol=symbol, leverage=leverage)

# 결과 기록
df = pd.DataFrame(columns=["step","price","side","profit","fee","capital_after"])

prev_price = None

# =======================
# 시뮬레이션 루프
# =======================
for step in range(n_steps):
    try:
        price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    except Exception as e:
        print(f"Step {step}: API 오류 - {e}", flush=True)
        price = prev_price if prev_price else 50000

    if prev_price is None:
        prev_price = price
        continue

    price_change = abs(price - prev_price)

    if price_change >= profit_threshold:
        # 가격 변동 감지 → 절댓값 수익 포지션 진입
        side = 'BUY' if price >= prev_price else 'SELL'

        # 포지션 생성
        try:
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=position_size
            )
            print(f"Step {step}: 포지션 진입 {side} {position_size} BTC", flush=True)
        except Exception as e:
            print(f"Step {step}: 주문 실패 - {e}", flush=True)
            continue

        # 즉시 청산
        close_side = 'SELL' if side == 'BUY' else 'BUY'
        try:
            close_order = client.futures_create_order(
                symbol=symbol,
                side=close_side,
                type='MARKET',
                quantity=position_size
            )
            # 절댓값 수익 계산 (레버리지 적용)
            profit = position_size * leverage * price_change
            fee = profit * fee_rate
            capital += profit - fee

            print(f"Step {step}: 포지션 청산, 수익={profit:.2f}, 수수료={fee:.2f}, 잔액={capital:.2f}", flush=True)

            df = pd.concat([df, pd.DataFrame([{
                "step": step,
                "price": price,
                "side": side,
                "profit": profit,
                "fee": fee,
                "capital_after": capital
            }])], ignore_index=True)

        except Exception as e:
            print(f"Step {step}: 청산 실패 - {e}", flush=True)

        prev_price = price  # 기준 가격 갱신

    time.sleep(sleep_sec)

# =======================
# 최종 요약
# =======================
print("\n==== Demo Summary ====", flush=True)
print(f"초기 자본: {50}$", flush=True)
print(f"최종 자본: {capital:.2f}$", flush=True)
print(f"총 수익: {capital - 50:.2f}$", flush=True)

print("\n==== 단계별 기록 ====", flush=True)
print(df, flush=True)
