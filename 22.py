import time
import sys
import signal
from binance.client import Client
from binance.enums import *
from decimal import Decimal, ROUND_UP
import math

print("Binance Futures - 0.1 USDT 극소 잔고 생존 모드 (최대한 시도 버전)")
print("테스트넷 사용? (y / n)   → 실전은 'n' 입력")
is_testnet = input().strip().lower() in ['y', 'yes']

api_key = input("API KEY: ").strip()
api_secret = input("API SECRET: ").strip()

client = Client(api_key, api_secret, testnet=is_testnet)

print(">>> TESTNET 데모" if is_testnet else ">>> MAINNET 실전 (0.1 USDT 극단 주의)")

# =============================================
# 극소 잔고 최적화 설정
# =============================================
SYMBOL = "1000BONKUSDT"          # 가장 작은 가격 심볼 (qty 극대화)
LEVERAGE = 75                    # 최대 레버리지로 최소 notional 강제 통과 시도
TRAILING_PCT = 0.15              # 0.15% 움직임만으로도 청산
MAX_HOLD_SEC = 2                 # 2초 넘으면 무조건 청산
MIN_NOTIONAL_USDT = 5.0          # Binance 최저선 강제 목표
FEE_RATE = 0.0005
MIN_BALANCE_TO_RUN = 0.1         # 이 아래면 스킵

total_profit = 0.0
cycle = 0
current_side = None
entry_price = 0.0
highest_price = 0.0
entry_time = 0

def adjust_qty(qty):
    return float(Decimal(str(qty)).to_integral_value(rounding=ROUND_UP))

def get_price():
    try:
        return float(client.futures_symbol_ticker(symbol=SYMBOL)['price'])
    except:
        return None

def get_balance():
    try:
        acc = client.futures_account()
        for a in acc['assets']:
            if a['asset'] == 'USDT':
                return float(a['availableBalance'])
        return 0.0
    except:
        return 0.0

def close_position():
    global current_side, entry_price, highest_price, entry_time
    try:
        positions = client.futures_position_information(symbol=SYMBOL)
        for pos in positions:
            amt = float(pos['positionAmt'])
            if amt != 0:
                side = SIDE_SELL if amt > 0 else SIDE_BUY
                q = abs(amt)
                client.futures_create_order(
                    symbol=SYMBOL,
                    side=side,
                    type=ORDER_TYPE_MARKET,
                    quantity=q,
                    reduceOnly=True
                )
                print(f"청산 완료: {q} units | 잔고 변동 반영 중...")
                break
        current_side = None
        entry_price = 0.0
        highest_price = 0.0
        entry_time = 0
    except Exception as e:
        print("청산 실패:", e)

signal.signal(signal.SIGINT, lambda s, f: (
    print("\n종료 → 모든 포지션 청산"),
    close_position(),
    print(f"최종 누적 수익: {total_profit:+.4f} USDT | 잔고: {get_balance():.4f}"),
    sys.exit(0)
))

# 초기 설정
try:
    client.futures_change_position_mode(dualSidePosition=False)
    client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)
    client.futures_change_margin_type(symbol=SYMBOL, marginType='ISOLATED')
    print(f"설정 완료: {LEVERAGE}x Isolated | 심볼: {SYMBOL}")
except Exception as e:
    print("설정 에러 (무시 가능):", e)

print("\n=== 0.1 USDT 극소 잔고 생존 모드 시작 ===")
print(f"Trailing 청산: {TRAILING_PCT}% | 최대 보유: {MAX_HOLD_SEC}초")
print("복리 적용 + 최소 notional 강제 → 0.1 USDT에서도 진입 시도")
print(f"현재 잔고: {get_balance():.4f} USDT")

while True:
    cycle += 1
    print(f"\n--- 사이클 {cycle} ---")

    try:
        balance = get_balance()
        if balance < MIN_BALANCE_TO_RUN:
            print(f"잔고 {balance:.4f} < {MIN_BALANCE_TO_RUN} USDT → 30초 대기")
            time.sleep(30)
            continue

        price = get_price()
        if not price:
            time.sleep(5)
            continue

        print(f"현재 가격: {price:.8f} | 잔고: {balance:.4f} USDT")

        # 극소 잔고용 강제 최소 qty 계산 (5 USDT notional 확보)
        min_qty_needed = math.ceil(MIN_NOTIONAL_USDT * 1.02 / price)  # 2% 여유
        qty = min_qty_needed

        # 잔고가 조금 더 있을 때만 복리 확대
        if balance > 1.0:
            position_value = balance * 0.40 * LEVERAGE  # 40% 사용
            qty_complex = position_value / price
            qty = max(qty, qty_complex)
            qty = adjust_qty(qty)

        notional = qty * price
        print(f"qty: {qty} | notional ${notional:.4f}")

        if notional < MIN_NOTIONAL_USDT:
            print("notional 부족 → 스킵 (레버리지/심볼 변경 필요)")
            time.sleep(10)
            continue

        # 현재 포지션 확인
        positions = client.futures_position_information(symbol=SYMBOL)
        pos_amt = 0.0
        pos_entry_price = 0.0
        for pos in positions:
            if pos['symbol'] == SYMBOL:
                pos_amt = float(pos['positionAmt'])
                pos_entry_price = float(pos['entryPrice'])
                break

        if pos_amt == 0:
            client.futures_create_order(
                symbol=SYMBOL,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            current_side = 'LONG'
            entry_price = price
            highest_price = price
            entry_time = time.time()
            print(f"신규 LONG 진입 @ {entry_price:.8f} | qty {qty}")
            time.sleep(0.3)
            continue

        # trailing + 시간 초과 체크
        if price > highest_price:
            highest_price = price

        trailing_stop = highest_price * (1 - TRAILING_PCT / 100)

        if price <= trailing_stop or (time.time() - entry_time) > MAX_HOLD_SEC:
            close_side = SIDE_SELL if current_side == 'LONG' else SIDE_BUY
            client.futures_create_order(
                symbol=SYMBOL,
                side=close_side,
                type=ORDER_TYPE_MARKET,
                quantity=abs(pos_amt),
                reduceOnly=True
            )

            gross = abs(price - pos_entry_price) * abs(pos_amt)
            fees = (pos_entry_price + price) * abs(pos_amt) * FEE_RATE
            net = gross - fees
            total_profit += net

            print(f"청산 완료 ({'Trailing' if price <= trailing_stop else '시간 초과'}) | Net {net:+.6f} USDT")
            print(f"누적 수익: {total_profit:+.4f} USDT | 잔고: {get_balance():.4f}")
            current_side = None
            time.sleep(0.5)
            continue

        time.sleep(0.2)  # 루프 매우 빠르게

    except Exception as e:
        print("에러:", str(e))
        time.sleep(5)
