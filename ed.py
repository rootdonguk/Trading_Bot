from binance.client import Client
import time, math

# =======================
# 1. 기본 설정
# =======================
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

client = Client(API_KEY, API_SECRET)

SYMBOL = "1000PEPEUSDT"
LEVERAGE = 20
BASE_MARGIN_RATIO = 0.05   # 기본 5% (작게 시작, 배수로 증폭)

# =======================
# 2. 유틸
# =======================
def sync_time():
    server_time = client.get_server_time()["serverTime"]
    client.timestamp_offset = server_time - int(time.time() * 1000)

def get_balance():
    for a in client.futures_account()["assets"]:
        if a["asset"] == "USDT":
            return float(a["availableBalance"])
    return 0.0

def get_price():
    return float(client.futures_symbol_ticker(symbol=SYMBOL)["price"])

def contract_value(price):
    return price * 1000  # 1000PEPE

# =======================
# 3. 🔥 네가 확정한 공식 (그대로)
# =======================
def volatility_boost(price_change):
    return 1 + math.log10(max(price_change, 0.1))

def momentum_boost(streak):
    return 1 + (streak * 0.1)

def compound_boost(capital):
    return math.sqrt(max(capital, 1) / 50)

def total_boost(price_change, streak, capital):
    return (
        volatility_boost(price_change)
        * momentum_boost(streak)
        * compound_boost(capital)
    )

# =======================
# 4. 초기화
# =======================
sync_time()
client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)

prev_price = None
streak = 0

print("=" * 60)
print(f"💰 시작 잔고: {get_balance():.2f} USDT")
print("🔥 조건미달 제거 / 최소 1계약 강제")
print("=" * 60)

# =======================
# 5. 메인 루프
# =======================
try:
    while True:
        price = get_price()
        balance = get_balance()

        if prev_price is None:
            prev_price = price
            time.sleep(0.5)
            continue

        # 🔥 방향 무관 — 움직임 자체가 트리거
        price_change = abs(price - prev_price)

        # 움직임이 없으면 스킵
        if price_change == 0:
            time.sleep(0.5)
            continue

        # 🔥 배수 계산
        boost = total_boost(price_change, streak, balance)

        # 🔥 증거금 사용 비율
        margin_ratio = min(BASE_MARGIN_RATIO * boost, 0.5)
        margin = balance * margin_ratio

        # 🔥 수량 계산
        raw_qty = int((margin * LEVERAGE) / contract_value(price))

        # 🔥 핵심: 무조건 최소 1계약
        min_notional = 5.0
        contract_val = contract_value(price)

        min_qty_notional = math.ceil(min_notional / contract_val)

        qty = max(1, raw_qty, min_qty_notional)


        # 방향은 그냥 직전 대비 (의미 없음, 형식용)
        side = "BUY" if price > prev_price else "SELL"

        try:
            print(
                f"\n🚀 체결 | 변동 ${price_change:.6f}"
                f" | 배수 {boost:.2f}"
                f" | 수량 {qty}"
            )

            # 진입
            client.futures_create_order(
                symbol=SYMBOL,
                side=side,
                type="MARKET",
                quantity=qty
            )

            time.sleep(0.4)

            # 즉시 청산
            client.futures_create_order(
                symbol=SYMBOL,
                side="SELL" if side == "BUY" else "BUY",
                type="MARKET",
                quantity=qty
            )

            streak += 1
            print("✅ 체결 완료")

        except Exception as e:
            streak = 0
            print(f"❌ 실패: {e}")

        prev_price = price
        time.sleep(1)

except KeyboardInterrupt:
    print("\n👋 종료")
