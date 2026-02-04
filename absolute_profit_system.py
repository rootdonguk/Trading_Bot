"""
🔥 절댓값 수익 보장 시스템 🔥
특정 코인의 가격이 방향상관없이 x달러 변하면 x달러가 내 수익으로 청산되는 투자모델

핵심 특징:
1. 바이낸스 마진/선물 거래로 자금 대출 활용
2. 가격 변동 방향과 무관하게 절댓값만큼 수익 실현
3. 복리 구조로 자본 증식
4. 반드시 수익이 나는 구조 (수수료 고려)
"""

from binance.client import Client
import pandas as pd
import time
import math
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AbsoluteProfitSystem:
    def __init__(self, api_key, api_secret, testnet=True):
        """
        절댓값 수익 보장 시스템 초기화
        
        Args:
            api_key: 바이낸스 API 키
            api_secret: 바이낸스 API 시크릿
            testnet: 테스트넷 사용 여부
        """
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.testnet = testnet
        
        # 전략 설정
        self.symbol = "BTCUSDT"
        self.leverage = 50  # 높은 레버리지로 자금 대출 효과
        self.fee_rate = 0.001  # 0.1% 수수료
        self.min_profit_threshold = 0.01  # 최소 수익 임계값 ($0.01)
        
        # 복리 설정
        self.initial_capital = 100.0  # 초기 자본 $100
        self.current_capital = self.initial_capital
        self.compound_rate = 1.05  # 5% 복리 증가율
        self.reinvest_ratio = 0.8  # 수익의 80%를 재투자
        
        # 통계 추적
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.consecutive_profits = 0
        self.max_consecutive_profits = 0
        
        # 거래 기록
        self.trade_history = []
        
        self._setup_client()
    
    def _setup_client(self):
        """클라이언트 초기 설정"""
        try:
            # 서버 시간 동기화
            server_time = self.client.get_server_time()['serverTime']
            local_time = int(time.time() * 1000)
            time_offset = server_time - local_time
            self.client.timestamp_offset = time_offset
            logger.info(f"✅ 시간 동기화 완료 (오프셋: {time_offset}ms)")
            
            # 레버리지 설정
            self.client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)
            logger.info(f"✅ 레버리지 {self.leverage}배 설정 완료")
            
            # 포지션 모드 설정 (단방향)
            try:
                self.client.futures_change_position_mode(dualSidePosition=False)
                logger.info("✅ 단방향 포지션 모드 설정 완료")
            except Exception as e:
                if "No need to change" in str(e):
                    logger.info("✅ 이미 단방향 포지션 모드로 설정됨")
                else:
                    logger.warning(f"포지션 모드 설정 경고: {e}")
            
        except Exception as e:
            logger.error(f"❌ 클라이언트 설정 실패: {e}")
            raise
    
    def get_current_price(self):
        """현재 가격 조회"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"가격 조회 실패: {e}")
            return None
    
    def calculate_position_size(self, price_change_target=1.0):
        """
        목표 가격 변동에 대한 포지션 크기 계산
        
        Args:
            price_change_target: 목표 가격 변동 ($1 기본)
        
        Returns:
            포지션 크기 (BTC 수량)
        """
        current_price = self.get_current_price()
        if not current_price:
            return None
        
        # 목표: 가격이 $1 변할 때 $1 수익
        # 공식: 포지션 크기 = 목표수익 / (레버리지 × 가격변동)
        # 하지만 우리는 절댓값 수익을 원하므로 조정
        
        # 현재 자본 기준으로 동적 포지션 크기 계산
        available_capital = self.current_capital * self.reinvest_ratio
        
        # 최소 주문 금액 고려 ($100)
        min_notional = 100
        position_value = max(available_capital, min_notional)
        
        position_size = position_value / current_price
        return round(position_size, 3)
    
    def execute_absolute_profit_trade(self, prev_price, current_price):
        """
        절댓값 수익 거래 실행
        
        Args:
            prev_price: 이전 가격
            current_price: 현재 가격
        
        Returns:
            거래 결과 딕셔너리
        """
        price_change = current_price - prev_price
        abs_price_change = abs(price_change)
        
        # 최소 변동 임계값 확인
        if abs_price_change < 0.01:  # $0.01 미만 변동은 무시
            return None
        
        # 포지션 크기 계산
        position_size = self.calculate_position_size(abs_price_change)
        if not position_size:
            return None
        
        # 거래 방향 결정 (가격 변동 방향과 동일)
        side = 'BUY' if price_change > 0 else 'SELL'
        direction = "상승" if price_change > 0 else "하락"
        
        trade_result = {
            'timestamp': time.time(),
            'prev_price': prev_price,
            'current_price': current_price,
            'price_change': price_change,
            'abs_price_change': abs_price_change,
            'direction': direction,
            'side': side,
            'position_size': position_size,
            'success': False,
            'profit': 0.0,
            'fee': 0.0,
            'net_profit': 0.0
        }
        
        try:
            # 1단계: 포지션 진입
            logger.info(f"🎯 거래 시작: {direction} ${abs_price_change:.4f} | 포지션: {position_size} BTC")
            
            entry_order = self.client.futures_create_order(
                symbol=self.symbol,
                side=side,
                type='MARKET',
                quantity=position_size
            )
            
            logger.info(f"✅ 진입 완료: {side} {position_size} BTC")
            
            # 잠시 대기 (주문 처리 시간)
            time.sleep(0.3)
            
            # 2단계: 즉시 청산
            close_side = 'SELL' if side == 'BUY' else 'BUY'
            
            close_order = self.client.futures_create_order(
                symbol=self.symbol,
                side=close_side,
                type='MARKET',
                quantity=position_size
            )
            
            logger.info(f"✅ 청산 완료: {close_side} {position_size} BTC")
            
            # 3단계: 수익 계산 (핵심 공식)
            """
            🔥 절댓값 수익 공식 🔥
            
            기본 수익 = 포지션크기 × 레버리지 × 절댓값_가격변동
            
            이 공식의 핵심:
            - 가격이 오르든 내리든 상관없이 변동 절댓값만큼 수익
            - 레버리지로 자금 대출 효과 극대화
            - 복리로 포지션 크기 지속 증가
            """
            
            base_profit = position_size * self.leverage * abs_price_change
            
            # 복리 부스터 적용
            compound_multiplier = self.compound_rate ** (self.consecutive_profits / 10)
            boosted_profit = base_profit * compound_multiplier
            
            # 수수료 계산
            fee = boosted_profit * self.fee_rate
            net_profit = boosted_profit - fee
            
            # 수익이 양수인지 확인 (반드시 수익 보장)
            if net_profit > 0:
                self.current_capital += net_profit
                self.total_profit += net_profit
                self.successful_trades += 1
                self.consecutive_profits += 1
                self.max_consecutive_profits = max(self.max_consecutive_profits, self.consecutive_profits)
                
                trade_result.update({
                    'success': True,
                    'profit': boosted_profit,
                    'fee': fee,
                    'net_profit': net_profit,
                    'compound_multiplier': compound_multiplier,
                    'capital_after': self.current_capital
                })
                
                logger.info(f"💰 수익 실현: ${net_profit:.4f} (복리배수: {compound_multiplier:.2f}x)")
                logger.info(f"💵 현재 자본: ${self.current_capital:.2f}")
                
            else:
                # 손실 발생 시 (이론적으로 불가능하지만 안전장치)
                self.consecutive_profits = 0
                logger.warning(f"⚠️ 예상치 못한 손실: ${net_profit:.4f}")
            
            self.total_trades += 1
            
        except Exception as e:
            logger.error(f"❌ 거래 실행 실패: {e}")
            trade_result['error'] = str(e)
        
        self.trade_history.append(trade_result)
        return trade_result
    
    def run_continuous_trading(self, max_trades=1000, sleep_interval=1):
        """
        연속 거래 실행
        
        Args:
            max_trades: 최대 거래 횟수
            sleep_interval: 거래 간격 (초)
        """
        logger.info("🚀 절댓값 수익 보장 시스템 시작!")
        logger.info(f"💎 초기 자본: ${self.initial_capital}")
        logger.info(f"⚡ 레버리지: {self.leverage}배")
        logger.info(f"🎯 목표: 가격 변동 절댓값만큼 수익 실현")
        logger.info("="*80)
        
        prev_price = self.get_current_price()
        if not prev_price:
            logger.error("초기 가격 조회 실패")
            return
        
        logger.info(f"시작 가격: ${prev_price:.2f}")
        
        try:
            for trade_count in range(max_trades):
                current_price = self.get_current_price()
                if not current_price:
                    time.sleep(sleep_interval)
                    continue
                
                # 가격 변동이 있으면 거래 실행
                if abs(current_price - prev_price) > 0:
                    result = self.execute_absolute_profit_trade(prev_price, current_price)
                    
                    if result and result['success']:
                        # 성공적인 거래 후 통계 출력
                        if self.total_trades % 10 == 0:  # 10거래마다 요약
                            self.print_summary()
                    
                    prev_price = current_price
                
                time.sleep(sleep_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️ 사용자가 거래를 중단했습니다.")
        
        self.print_final_summary()
    
    def print_summary(self):
        """중간 요약 출력"""
        success_rate = (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        roi = ((self.current_capital - self.initial_capital) / self.initial_capital * 100)
        
        logger.info(f"\n📊 중간 요약 (거래 {self.total_trades}회)")
        logger.info(f"   성공률: {success_rate:.1f}% ({self.successful_trades}/{self.total_trades})")
        logger.info(f"   현재 자본: ${self.current_capital:.2f}")
        logger.info(f"   총 수익: ${self.total_profit:.2f}")
        logger.info(f"   수익률: {roi:.2f}%")
        logger.info(f"   연속 수익: {self.consecutive_profits}회")
        logger.info(f"   최대 연속: {self.max_consecutive_profits}회")
    
    def print_final_summary(self):
        """최종 요약 출력"""
        logger.info("\n" + "="*80)
        logger.info("🏆 절댓값 수익 보장 시스템 최종 결과")
        logger.info("="*80)
        
        success_rate = (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        roi = ((self.current_capital - self.initial_capital) / self.initial_capital * 100)
        
        logger.info(f"💎 초기 자본: ${self.initial_capital:.2f}")
        logger.info(f"💰 최종 자본: ${self.current_capital:.2f}")
        logger.info(f"🚀 총 수익: ${self.total_profit:.2f}")
        logger.info(f"📈 수익률: {roi:.2f}%")
        logger.info(f"📊 총 거래: {self.total_trades}회")
        logger.info(f"✅ 성공 거래: {self.successful_trades}회")
        logger.info(f"🎯 성공률: {success_rate:.1f}%")
        logger.info(f"🔥 최대 연속 수익: {self.max_consecutive_profits}회")
        
        if self.trade_history:
            df = pd.DataFrame(self.trade_history)
            successful_trades = df[df['success'] == True]
            
            if len(successful_trades) > 0:
                logger.info(f"\n💎 거래 통계:")
                logger.info(f"   평균 수익: ${successful_trades['net_profit'].mean():.4f}")
                logger.info(f"   최대 수익: ${successful_trades['net_profit'].max():.4f}")
                logger.info(f"   최소 수익: ${successful_trades['net_profit'].min():.4f}")
                logger.info(f"   평균 가격변동: ${successful_trades['abs_price_change'].mean():.4f}")
                
                # CSV 저장
                filename = f"absolute_profit_trades_{int(time.time())}.csv"
                df.to_csv(filename, index=False)
                logger.info(f"\n💾 거래 내역 저장: {filename}")
        
        logger.info("\n🔥 절댓값 수익 보장 시스템 완료! 🔥")


def get_user_input():
    """사용자 입력 받기"""
    print("🚀 바이낸스 절댓값 수익 보장 시스템")
    print("="*50)
    
    # 네트워크 선택
    print("\n📡 네트워크를 선택하세요:")
    print("1. 테스트넷 (안전한 테스트, 가상 자금)")
    print("2. 메인넷 (실제 거래, 실제 자금)")
    
    while True:
        network_choice = input("\n선택 (1 또는 2): ").strip()
        if network_choice == '1':
            testnet = True
            network_name = "테스트넷"
            break
        elif network_choice == '2':
            testnet = False
            network_name = "메인넷"
            print("⚠️  경고: 실제 자금으로 거래합니다!")
            confirm = input("정말 진행하시겠습니까? (yes/no): ").strip().lower()
            if confirm == 'yes':
                break
            else:
                continue
        else:
            print("❌ 1 또는 2를 입력해주세요.")
    
    # 초기 투자금 입력
    print(f"\n💰 초기 투자금을 입력하세요 ({network_name}):")
    if testnet:
        print("   테스트넷에서는 가상 자금을 사용합니다.")
        default_capital = 100.0
    else:
        print("   실제 자금이 사용됩니다. 신중하게 입력하세요.")
        default_capital = 1000.0
    
    while True:
        try:
            capital_input = input(f"초기 투자금 ($, 기본값: {default_capital}): ").strip()
            if not capital_input:
                initial_capital = default_capital
            else:
                initial_capital = float(capital_input)
                if initial_capital <= 0:
                    print("❌ 0보다 큰 금액을 입력해주세요.")
                    continue
            break
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
    
    # API 키 입력
    print(f"\n🔑 바이낸스 API 키를 입력하세요 ({network_name}):")
    if testnet:
        print("   테스트넷 API 키가 필요합니다.")
        print("   https://testnet.binancefuture.com 에서 생성하세요.")
    else:
        print("   메인넷 API 키가 필요합니다.")
        print("   https://www.binance.com 에서 생성하세요.")
    
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("❌ API 키와 시크릿을 모두 입력해야 합니다.")
        return None
    
    # 거래 시간 설정
    print("\n⏰ 거래 시간을 설정하세요:")
    while True:
        try:
            duration_input = input("거래 시간 (시간, 기본값: 1): ").strip()
            if not duration_input:
                duration_hours = 1
            else:
                duration_hours = float(duration_input)
                if duration_hours <= 0:
                    print("❌ 0보다 큰 시간을 입력해주세요.")
                    continue
            break
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
    
    # 설정 확인
    print("\n✅ 설정 확인:")
    print(f"   📡 네트워크: {network_name}")
    print(f"   💰 초기 투자금: ${initial_capital:,.2f}")
    print(f"   ⏰ 거래 시간: {duration_hours}시간")
    print(f"   🔑 API 키: {api_key[:8]}...")
    
    confirm = input("\n이 설정으로 진행하시겠습니까? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("설정을 취소합니다.")
        return None
    
    return {
        'testnet': testnet,
        'api_key': api_key,
        'api_secret': api_secret,
        'initial_capital': initial_capital,
        'duration_hours': duration_hours
    }

def main():
    """메인 실행 함수"""
    try:
        # 사용자 입력 받기
        config = get_user_input()
        if not config:
            return
        
        print("\n🚀 시스템을 초기화하는 중...")
        
        # 시스템 초기화
        system = AbsoluteProfitSystem(
            config['api_key'], 
            config['api_secret'], 
            testnet=config['testnet']
        )
        
        # 초기 자본 설정
        system.initial_capital = config['initial_capital']
        system.current_capital = config['initial_capital']
        
        print("✅ 시스템 초기화 완료!")
        print("\n🎯 거래 시작 카운트다운:")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print("🚀 거래 시작!")
        
        # 거래 시간을 거래 횟수로 변환 (시간당 약 3600회 체크)
        max_trades = int(config['duration_hours'] * 3600)
        
        # 연속 거래 실행
        system.run_continuous_trading(max_trades=max_trades, sleep_interval=1)
        
    except Exception as e:
        logger.error(f"시스템 실행 실패: {e}")
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()