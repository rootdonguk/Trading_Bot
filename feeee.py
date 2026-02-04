from binance.client import Client
import time, math

# =======================
# 1. 기본 설정
# =======================
API_KEY = ""
API_SECRET = ""

client = Client(API_KEY, API_SECRET)

SYMBOL = "1000PEPEUSDT"
LEVERAGE = 20
BASE_MARGIN_RATIO = 0.1   # 기본 10%만 사용 (공식으로 증폭)

# =======================
# 2. 유틸 함수
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

def get_contract_value(price):
    return price * 1000  # 1000PEPE 계약

# =======================
# 3. 🔥 혁명 공식 (확정본)
# =======================
def volatility_multiplier(price_change):
    return 1 + math.log10(max(price_change, 0.1))

def momentum_multiplier(win_streak):
    return 1 + (win_streak * 0.1)

def compound_multiplier(capital):
    return math.sqrt(max(capital, 1) / 50)

def total_multiplier(price_change, win_streak, capital):
    return (
        volatility_multiplier(price_change)
        * momentum_multiplier(win_streak)
        * compound_multiplier(capital)
    )

# =======================
# 4. 초기 세팅
# =======================
sync_time()
client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)

print("✅ 시스템 준비 완료")
print(f"💰 시작 잔고: {get_balance():.2f} USDT")
print("=" * 60)

# =======================
# 5. 메인 루프
# =======================
prev_price = None
win_streak = 0

try:
    while True:
        price = get_price()
        balance = get_balance()

        if prev_price is None:
            prev_price = price
            time.sleep(0.5)
            continue

        price_change = abs(price - prev_price)
        direction = "BUY" if price > prev_price else "SELL"

        # 🔥 혁명 배수 계산
        boost = total_multiplier(price_change, win_streak, balance)

        # 🔥 실제 사용 증거금 비율 (공식 반영)
        margin_ratio = min(BASE_MARGIN_RATIO * boost, 0.5)  # 최대 50% 제한
        margin_to_use = balance * margin_ratio

        contract_value = get_contract_value(price)
        qty = int((margin_to_use * LEVERAGE) / contract_value)

        if qty < 1:
            print("⚠️ 조건 미달 — 대기")
            time.sleep(1)
            prev_price = price
            continue

        try:
            print(f"\n🚀 진입 | {direction} | 수량 {qty}")
            print(f"⚡ 배수 {boost:.2f} | 증거금 비율 {margin_ratio:.2f}")

            client.futures_create_order(
                symbol=SYMBOL,
                side=direction,
                type="MARKET",
                quantity=qty
            )

            time.sleep(0.5)

            close_side = "SELL" if direction == "BUY" else "BUY"
            client.futures_create_order(
                symbol=SYMBOL,
                side=close_side,
                type="MARKET",
                quantity=qty
            )

            win_streak += 1
            print("✅ 체결 성공")

        except Exception as e:
            win_streak = 0
            print(f"❌ 실패: {e}")

        prev_price = price
        time.sleep(1)

except KeyboardInterrupt:
    print("\n👋 종료")
