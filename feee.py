from binance.client import Client
import time
import math

# =======================
# 1. Binance 연결 설정
# =======================
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"
client = Client(api_key, api_secret)

# =======================
# 2. 전략 설정
# =======================
symbol = "1000PEPEUSDT"
leverage = 50          # 레버리지 50배
ACCUMULATION_THRESHOLD = 5.0  # $5.0 누적 시 실제 거래 시도
PRICE_MULTIPLIER = 500000.0   # 수익 증폭기

# 변수 초기화
accumulated_amount = 0
virtual_trades = 0

def get_futures_balance():
    try:
        account_info = client.futures_account()
        for asset in account_info['assets']:
            if asset['asset'] == 'USDT':
                return float(asset['availableBalance'])
    except Exception as e:
        print(f"❌ 잔고 조회 실패: {e}")
        return 0.0
    return 0.0

# 서버 시간 동기화 및 초기 세팅
try:
    client.timestamp_offset = client.get_server_time()['serverTime'] - int(time.time() * 1000)
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    client.futures_change_position_mode(dualSidePosition=False) # 단방향 모드 고정
except:
    pass

print(f"✅ 시스템 가동: {symbol} (레버리지 {leverage}배)")
print(f"💰 현재 주문 가능 잔액: ${get_futures_balance()}")

# 초기 가격 설정
try:
    prev_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
except Exception as e:
    print(f"❌ 초기 가격 조회 실패: {e}")
    exit()

# =======================
# 3. 메인 루프
# =======================
try:
    while True:
        try:
            # 현재가 조회
            curr_ticker = client.futures_symbol_ticker(symbol=symbol)
            curr_price = float(curr_ticker['price'])
            price_change = curr_price - prev_price
            
            if price_change != 0:
                virtual_trades += 1
                # 가상 수익 누적 (움직이면 무조건 플러스)
                v_profit = abs(price_change) * PRICE_MULTIPLIER
                accumulated_amount += v_profit
                
                print(f"📈 {curr_price:.7f} | 누적에너지: ${accumulated_amount:.4f} / ${ACCUMULATION_THRESHOLD}")

                # 🔥 임계점 돌파 시 실제 거래 실행
                if accumulated_amount >= ACCUMULATION_THRESHOLD:
                    wallet = get_futures_balance()
                    buying_power = wallet * leverage
                    
                    # 바이낸스 최소 주문 금액은 보통 $5 이상이어야 함
                    if buying_power >= 5.0:
                        # 1000PEPE는 정수 수량만 가능
                        quantity = int(buying_power / curr_price)
                        side = 'BUY' if price_change > 0 else 'SELL'
                        
                        if quantity > 0:
                            print(f"🚀 [에너지 폭발] 실제 주문 실행: {side} {quantity}개")
                            
                            # 시장가 진입
                            client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
                            time.sleep(0.5) # 체결 대기
                            
                            # 즉시 청산
                            close_side = 'SELL' if side == 'BUY' else 'BUY'
                            client.futures_create_order(symbol=symbol, side=close_side, type='MARKET', quantity=quantity)
                            
                            print(f"💰 혁명 성공! 에너지 실현 완료.")
                            accumulated_amount = 0 # 에너지 리셋
                        else:
                            print("⚠️ 계산된 주문 수량이 0입니다.")
                    else:
                        # 10번마다 잔액 부족 경고 메시지 출력
                        if virtual_trades % 10 == 0:
                            print(f"⚠️ 에너지 응축 중... (현재 구매력 ${buying_power:.2f} / 필요 $5.0)")

                prev_price = curr_price
            
            time.sleep(0.5) # 0.5초 간격 감시

        except Exception as e:
            # API 에러 메시지 상세 출력
            print(f"⚠️ 대기 중 (에러): {e}")
            time.sleep(2)

except KeyboardInterrupt:
    print("\n👋 혁명 일시 중단. 프로그램을 안전하게 종료합니다.")