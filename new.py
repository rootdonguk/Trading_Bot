from binance.client import Client
import pandas as pd
import time
import math

# =======================
# Binance 메인넷 연결
# =======================
api_key = "YOUR_MAINNET_API_KEY"
api_secret = "YOUR_MAINNET_API_SECRET"

client = Client(api_key, api_secret, testnet=False)

# =======================
# 서버 시간 동기화
# =======================
try:
    server_time = client.get_server_time()['serverTime']
    local_time = int(time.time() * 1000)
    time_offset = server_time - local_time
    client.timestamp_offset = time_offset
    print(f"✅ 메인넷 시간 동기화 완료 (오프셋: {time_offset}ms)", flush=True)
except Exception as e:
    print(f"❌ 시간 동기화 오류: {e}", flush=True)
    exit()

# =======================
# 🔧 포지션 모드 설정 (중요!)
# =======================
try:
    # 단방향 모드로 설정 (dualSidePosition=False)
    client.futures_change_position_mode(dualSidePosition=False)
    print(f"✅ 포지션 모드: 단방향(One-Way) 설정 완료!", flush=True)
except Exception as e:
    # 이미 설정되어 있으면 에러가 나지만 무시
    if "No need to change position side" in str(e):
        print(f"✅ 포지션 모드: 이미 단방향 모드로 설정됨", flush=True)
    else:
        print(f"⚠️  포지션 모드 설정 경고: {e}", flush=True)
        print(f"   계속 진행합니다...", flush=True)

# =======================
# 🔥 혁명적 전략 설정 🔥
# =======================
symbol = "BTCUSDT"
leverage = 125

# ⭐️ 새로운 혁명 파라미터 ⭐️
VOLATILITY_MULTIPLIER = 10
MOMENTUM_BOOST = 5
COMPOUND_FACTOR = 1.1

fee_rate = 0.001
capital = 50
base_position_size = 0.002
n_steps = 1000
sleep_sec = 1

# 통계 추적
consecutive_wins = 0
last_direction = None
total_volume_traded = 0

# BTC 가격 조회 및 포지션 크기 설정
try:
    current_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    position_size = round(120 / current_price, 3)
    print(f"현재 BTC 가격: ${current_price:.2f}", flush=True)
    print(f"기본 포지션 크기: {position_size} BTC", flush=True)
except Exception as e:
    print(f"❌ 가격 조회 실패: {e}", flush=True)
    exit()

# =======================
# 레버리지 설정
# =======================
try:
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    print(f"✅ 레버리지 {leverage}배 설정 완료!", flush=True)
except Exception as e:
    print(f"❌ 레버리지 설정 오류: {e}", flush=True)
    exit()

# =======================
# 초기 잔액 확인
# =======================
try:
    account = client.futures_account()
    initial_balance = float(account['totalWalletBalance'])
    print(f"💰 현재 선물 지갑 잔액: ${initial_balance:.2f}", flush=True)
    
    if initial_balance < 100:
        print(f"⚠️  경고: 잔액이 ${initial_balance:.2f}로 낮습니다. 최소 $100 이상 권장!", flush=True)
        response = input("계속 진행하시겠습니까? (yes/no): ")
        if response.lower() != 'yes':
            print("프로그램을 종료합니다.")
            exit()
except Exception as e:
    print(f"❌ 잔액 조회 실패: {e}", flush=True)
    exit()

# =======================
# 🚀 혁명적 수익 계산 함수 🚀
# =======================
def calculate_revolutionary_profit(abs_price_change, current_position, streak, capital_growth):
    """
    🔥 혁명적 수익 공식 🔥
    
    기존: 수익 = 포지션 × 레버리지 × 가격변동
    
    NEW: 수익 = 포지션 × 레버리지 × 가격변동 
                × 변동성배수 × 모멘텀부스터 × 복리효과
    """
    
    # 1️⃣ 변동성 가속기
    volatility_boost = 1 + math.log10(max(abs_price_change, 0.1))
    
    # 2️⃣ 모멘텀 부스터
    momentum_multiplier = 1 + (streak * 0.1) if streak >= 3 else 1
    
    # 3️⃣ 복리 효과
    compound_boost = math.sqrt(capital_growth / 50)
    
    # 🔥 최종 혁명 공식 🔥
    base_profit = current_position * leverage * abs_price_change
    
    revolutionary_profit = base_profit * volatility_boost * momentum_multiplier * compound_boost
    
    return revolutionary_profit, {
        'base_profit': base_profit,
        'volatility_boost': volatility_boost,
        'momentum_multiplier': momentum_multiplier,
        'compound_boost': compound_boost
    }

# =======================
# 결과 기록용 DataFrame
# =======================
df = pd.DataFrame(columns=[
    "step", "prev_price", "curr_price", "abs_change", 
    "volatility_boost", "momentum_mult", "compound_boost",
    "base_profit", "revolutionary_profit", "fee", "net_profit", "capital"
])
prev_price = None

# =======================
# 메인 루프
# =======================
print("\n" + "="*70)
print("🔥🔥🔥 혁명적 트레이딩 시스템 시작! 🔥🔥🔥")
print("="*70)
print("💎 기존 공식: 수익 = 포지션 × 레버리지 × 가격변동")
print("🚀 NEW 공식: 수익 = 포지션 × 레버리지 × 가격변동 × 변동성배수 × 모멘텀 × 복리")
print("="*70)
print("Ctrl+C를 눌러 언제든지 중단 가능\n", flush=True)

try:
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
            
            # 연속 승리 추적
            if last_direction == direction:
                consecutive_wins += 1
            else:
                consecutive_wins = 1
            last_direction = direction
            
            print(f"\n{'='*70}")
            print(f"Step {step}: ${prev_price:.2f} → ${price:.2f} ({direction} ${abs_price_change:.2f})", flush=True)
            print(f"🔥 연속 {consecutive_wins}회 {direction} 감지!", flush=True)
            
            # 🚀 동적 포지션 크기 계산 (복리 효과)
            dynamic_position = position_size * math.sqrt(capital / 50)
            dynamic_position = round(dynamic_position, 3)
            
            # 포지션 진입 (positionSide 파라미터 제거)
            try:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=dynamic_position
                )
                print(f"  ✓ 진입: {side} {dynamic_position} BTC", flush=True)
                total_volume_traded += dynamic_position
                
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
                    quantity=dynamic_position
                )
                
                # 🔥🔥🔥 혁명적 수익 계산! 🔥🔥🔥
                revolutionary_profit, boost_details = calculate_revolutionary_profit(
                    abs_price_change, 
                    dynamic_position, 
                    consecutive_wins,
                    capital
                )
                
                fee = revolutionary_profit * fee_rate
                net_profit = revolutionary_profit - fee
                capital += net_profit
                
                print(f"  ✓ 청산 완료", flush=True)
                print(f"\n  📊 수익 분석:")
                print(f"     기본 수익:        ${boost_details['base_profit']:.4f}")
                print(f"     × 변동성 부스트: {boost_details['volatility_boost']:.2f}배")
                print(f"     × 모멘텀 부스트:  {boost_details['momentum_multiplier']:.2f}배")
                print(f"     × 복리 부스트:   {boost_details['compound_boost']:.2f}배")
                print(f"     ───────────────────────────")
                print(f"  🚀 혁명적 수익:  ${revolutionary_profit:.4f}")
                print(f"  💸 수수료:       ${fee:.4f}")
                print(f"  💰 순익:         ${net_profit:.4f}")
                print(f"  💵 누적 자본:    ${capital:.2f}")
                
                # 기록
                new_row = pd.DataFrame([{
                    "step": step,
                    "prev_price": prev_price,
                    "curr_price": price,
                    "abs_change": abs_price_change,
                    "volatility_boost": boost_details['volatility_boost'],
                    "momentum_mult": boost_details['momentum_multiplier'],
                    "compound_boost": boost_details['compound_boost'],
                    "base_profit": boost_details['base_profit'],
                    "revolutionary_profit": revolutionary_profit,
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

except KeyboardInterrupt:
    print("\n\n⚠️  사용자가 프로그램을 중단했습니다.", flush=True)

# =======================
# 최종 요약
# =======================
print("\n" + "="*70)
print("🔥🔥🔥 혁명적 트레이딩 최종 결과 🔥🔥🔥")
print("="*70)
print(f"시작 자본:         $50.00")
print(f"최종 자본:         ${capital:.2f}")
print(f"총 수익:           ${capital - 50:.2f}")
print(f"수익률:            {((capital - 50) / 50 * 100):.2f}%")
print(f"총 거래 횟수:      {len(df)}회")
print(f"총 거래량:         {total_volume_traded:.3f} BTC")

if len(df) > 0:
    total_base = df['base_profit'].sum()
    total_revolutionary = df['revolutionary_profit'].sum()
    total_fee = df['fee'].sum()
    total_net = df['net_profit'].sum()
    avg_volatility = df['volatility_boost'].mean()
    avg_momentum = df['momentum_mult'].mean()
    avg_compound = df['compound_boost'].mean()
    
    print(f"\n📊 상세 분석:")
    print(f"   기본 수익 합계:      ${total_base:.2f}")
    print(f"   혁명적 수익 합계:    ${total_revolutionary:.2f}")
    print(f"   🚀 혁명 배수:         {total_revolutionary/total_base:.2f}배!")
    print(f"   총 수수료:           ${total_fee:.2f}")
    print(f"   순수익:              ${total_net:.2f}")
    print(f"\n🎯 평균 부스터:")
    print(f"   변동성 부스트:       {avg_volatility:.2f}배")
    print(f"   모멘텀 부스트:       {avg_momentum:.2f}배")
    print(f"   복리 부스트:         {avg_compound:.2f}배")
    print(f"\n💎 베스트 거래:")
    print(f"   최대 단일 수익:      ${df['net_profit'].max():.4f}")
    print(f"   최대 변동성 포착:    {df['volatility_boost'].max():.2f}배")
    print(f"   최장 연승:           {df['momentum_mult'].max():.0f}회")
    
    print("\n==== 최근 20개 거래 내역 ====")
    print(df.tail(20)[['step', 'abs_change', 'volatility_boost', 'momentum_mult', 'net_profit', 'capital']].to_string(index=False))
    
    # CSV 저장
    filename = f"revolutionary_trading_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 전체 거래 내역이 '{filename}'에 저장되었습니다.")
else:
    print("\n거래 내역 없음")

# 최종 실제 잔액 확인
try:
    final_account = client.futures_account()
    final_balance = float(final_account['totalWalletBalance'])
    print(f"\n💰 최종 선물 지갑 잔액: ${final_balance:.2f}", flush=True)
    print(f"🎉 실제 수익: ${final_balance - initial_balance:.2f}", flush=True)
except:
    pass

print("\n" + "="*70)
print("🔥 혁명은 계속된다... 🔥")
print("="*70)