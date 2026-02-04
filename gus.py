from binance.client import Client
import time, math

# =======================
# 1. 기본 설정
# =======================
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

client = Client(API_KEY, API_SECRET)

SYMBOL = "PEPEUSDT"  # Spot 마켓
BASE_MARGIN_RATIO = 0.05   # 잔고 5% 사용

# =======================
# 2. 유틸
# =======================
# 서버 시간 동기화
server_time = client.get_server_time()['serverTime']
local_time = int(time.time() * 1000)
client.timestamp_offset = server_time - local_time

# 잔고 조회
def get_balance():
    account = client.get_account(recvWindow=10000)  # recvWindow 늘림
    for a in account['balances']:
        if a['asset'] == 'USDT':
            return float(a['free'])
    return 0.0

def get_price():
    return float(client.get_symbol_ticker(symbol=SYMBOL)["price"])

def volatility_boost(price_change):
    return 1 + math.log10(max(price_change, 0.1))

def momentum_boost(streak):
    return 1 + (streak * 0.1)

def compound_boost(capital):
    return math.sqrt(max(capital, 1) / 50)

def total_boost(price_change, streak, capital):
    return volatility_boost(price_change) * momentum_boost(streak) * compound_boost(capital)

# =======================
# 3. 초기화
# =======================
prev_price = None
streak = 0

print("=" * 60)
print(f"💰 시작 잔고: {get_balance():.2f} USDT")
print("🔥 Spot용, 최소 주문 조건 제거")
print("=" * 60)

# =======================
# 4. 메인 루프
# =======================
try:
    while True:
        price = get_price()
        balance = get_balance()

        if prev_price is None:
            prev_price = price
            time.sleep(0.5)
            continue

        price_change = abs(price - prev_price)
        if price_change == 0:
            time.sleep(0.5)
            continue

        boost = total_boost(price_change, streak, balance)

        # 🔥 사용 금액
        invest_amount = balance * BASE_MARGIN_RATIO * boost
        invest_amount = max(invest_amount, 0.01)  # 최소 주문 0.01 USDT

        qty = invest_amount / price

        # Step size 적용
        info = client.get_symbol_info(SYMBOL)
        step_size = float([f for f in info['filters'] if f['filterType']=='LOT_SIZE'][0]['stepSize'])
        qty = math.floor(qty / step_size) * step_size

        # 최소 주문액 체크
        if qty * price < 0.01:  
            qty = step_size  # 최소 주문 단위 강제

        side = "BUY" if price > prev_price else "SELL"

        try:
            print(
                f"\n🚀 체결 | 변동 ${price_change:.6f} | 배수 {boost:.2f} | 금액 ${invest_amount:.2f} | 수량 {qty:.6f}"
            )

            if side == "BUY":
                client.order_market_buy(symbol=SYMBOL, quantity=qty)
            else:
                client.order_market_sell(symbol=SYMBOL, quantity=qty)

            streak += 1
            print("✅ 체결 완료")

        except Exception as e:
            streak = 0
            print(f"❌ 실패: {e}")

        prev_price = price
        time.sleep(1)

except KeyboardInterrupt:
    print("\n👋 종료")
