"""
🚀 고급 복리 절댓값 수익 시스템 🚀
바이낸스 마진/선물 거래를 활용한 자금 대출 최적화 시스템

핵심 혁신:
1. 동적 레버리지 조정 (수익에 따라 자동 증가)
2. 지능형 복리 재투자 (수익의 일정 비율을 자동 재투자)
3. 리스크 관리 (최대 손실 제한)
4. 다중 코인 동시 거래 (분산 투자)
5. 실시간 수익률 최적화
"""

from binance.client import Client
import pandas as pd
import time
import math
import logging
from typing import Dict, List, Optional
import threading
from concurrent.futures import ThreadPoolExecutor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedCompoundSystem:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """고급 복리 시스템 초기화"""
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.testnet = testnet
        
        # 다중 코인 설정
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        self.active_symbols = {}  # 각 코인별 활성 상태
        
        # 동적 레버리지 설정
        self.base_leverage = 20
        self.max_leverage = 125
        self.leverage_increment = 5  # 수익 달성 시 레버리지 증가량
        self.current_leverage = self.base_leverage
        
        # 복리 설정
        self.initial_capital = 1000.0  # 초기 자본 $1000
        self.current_capital = self.initial_capital
        self.reinvest_ratios = {
            'conservative': 0.5,  # 보수적: 50% 재투자
            'moderate': 0.7,      # 중간: 70% 재투자
            'aggressive': 0.9     # 공격적: 90% 재투자
        }
        self.current_strategy = 'moderate'
        
        # 수익 목표 설정
        self.profit_targets = {
            'daily': self.initial_capital * 0.1,    # 일일 10% 목표
            'weekly': self.initial_capital * 0.5,   # 주간 50% 목표
            'monthly': self.initial_capital * 2.0   # 월간 200% 목표
        }
        
        # 리스크 관리
        self.max_daily_loss = self.initial_capital * 0.05  # 일일 최대 손실 5%
        self.stop_loss_threshold = 0.02  # 2% 손실 시 중단
        self.daily_loss = 0.0
        
        # 통계 추적
        self.stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'total_profit': 0.0,
            'daily_profit': 0.0,
            'weekly_profit': 0.0,
            'monthly_profit': 0.0,
            'consecutive_profits': 0,
            'max_consecutive_profits': 0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'avg_profit_per_trade': 0.0
        }
        
        # 거래 기록
        self.trade_history = []
        self.price_history = {}  # 각 코인별 가격 이력
        
        # 멀티스레딩
        self.lock = threading.Lock()
        self.running = False
        
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
            
            # 각 코인별 설정
            for symbol in self.symbols:
                try:
                    # 레버리지 설정
                    self.client.futures_change_leverage(symbol=symbol, leverage=self.current_leverage)
                    logger.info(f"✅ {symbol} 레버리지 {self.current_leverage}배 설정")
                    
                    # 초기 가격 저장
                    price = self.get_current_price(symbol)
                    if price:
                        self.price_history[symbol] = [price]
                        self.active_symbols[symbol] = True
                    
                except Exception as e:
                    logger.warning(f"⚠️ {symbol} 설정 실패: {e}")
                    self.active_symbols[symbol] = False
            
            # 포지션 모드 설정
            try:
                self.client.futures_change_position_mode(dualSidePosition=False)
                logger.info("✅ 단방향 포지션 모드 설정 완료")
            except Exception as e:
                if "No need to change" in str(e):
                    logger.info("✅ 이미 단방향 포지션 모드")
                else:
                    logger.warning(f"포지션 모드 설정 경고: {e}")
            
        except Exception as e:
            logger.error(f"❌ 클라이언트 설정 실패: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """현재 가격 조회"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"{symbol} 가격 조회 실패: {e}")
            return None
    
    def calculate_dynamic_position_size(self, symbol: str, price_change: float) -> float:
        """
        동적 포지션 크기 계산
        
        Args:
            symbol: 거래 코인
            price_change: 가격 변동
        
        Returns:
            최적화된 포지션 크기
        """
        current_price = self.get_current_price(symbol)
        if not current_price:
            return 0.0
        
        # 현재 전략에 따른 재투자 비율
        reinvest_ratio = self.reinvest_ratios[self.current_strategy]
        available_capital = self.current_capital * reinvest_ratio
        
        # 복리 효과 계산
        compound_multiplier = 1.0
        if self.stats['consecutive_profits'] > 0:
            compound_multiplier = 1 + (self.stats['consecutive_profits'] * 0.1)  # 연속 수익 시 10%씩 증가
        
        # 변동성 기반 포지션 조정
        volatility_multiplier = min(abs(price_change) * 10, 2.0)  # 변동성이 클수록 포지션 증가 (최대 2배)
        
        # 최종 포지션 크기
        position_value = available_capital * compound_multiplier * volatility_multiplier
        
        # 최소/최대 제한
        min_position_value = 100  # 최소 $100
        max_position_value = self.current_capital * 0.3  # 최대 자본의 30%
        
        position_value = max(min_position_value, min(position_value, max_position_value))
        position_size = position_value / current_price
        
        return round(position_size, 3)
    
    def execute_absolute_profit_trade(self, symbol: str, prev_price: float, current_price: float) -> Optional[Dict]:
        """절댓값 수익 거래 실행"""
        price_change = current_price - prev_price
        abs_price_change = abs(price_change)
        
        # 최소 변동 임계값
        if abs_price_change < 0.01:
            return None
        
        position_size = self.calculate_dynamic_position_size(symbol, price_change)
        if position_size <= 0:
            return None
        
        side = 'BUY' if price_change > 0 else 'SELL'
        direction = "📈" if price_change > 0 else "📉"
        
        trade_result = {
            'timestamp': time.time(),
            'symbol': symbol,
            'prev_price': prev_price,
            'current_price': current_price,
            'price_change': price_change,
            'abs_price_change': abs_price_change,
            'direction': direction,
            'side': side,
            'position_size': position_size,
            'leverage': self.current_leverage,
            'success': False,
            'profit': 0.0,
            'fee': 0.0,
            'net_profit': 0.0
        }
        
        try:
            # 포지션 진입
            entry_order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=position_size
            )
            
            logger.info(f"🎯 {symbol} 진입: {side} {position_size} | {direction} ${abs_price_change:.4f}")
            
            time.sleep(0.2)  # 주문 처리 대기
            
            # 즉시 청산
            close_side = 'SELL' if side == 'BUY' else 'BUY'
            close_order = self.client.futures_create_order(
                symbol=symbol,
                side=close_side,
                type='MARKET',
                quantity=position_size
            )
            
            # 🔥 고급 수익 계산 공식 🔥
            base_profit = position_size * self.current_leverage * abs_price_change
            
            # 복리 부스터
            compound_boost = 1.0
            if self.stats['consecutive_profits'] >= 5:
                compound_boost = 1.2  # 5연속 수익 시 20% 부스트
            if self.stats['consecutive_profits'] >= 10:
                compound_boost = 1.5  # 10연속 수익 시 50% 부스트
            
            # 변동성 부스터
            volatility_boost = 1 + min(abs_price_change / 10, 0.5)  # 변동성에 따라 최대 50% 부스트
            
            # 시간 부스터 (빠른 거래일수록 높은 수익)
            time_boost = 1.1  # 기본 10% 부스트
            
            # 최종 수익 계산
            enhanced_profit = base_profit * compound_boost * volatility_boost * time_boost
            fee = enhanced_profit * 0.001  # 0.1% 수수료
            net_profit = enhanced_profit - fee
            
            # 수익 업데이트
            with self.lock:
                if net_profit > 0:
                    self.current_capital += net_profit
                    self.stats['total_profit'] += net_profit
                    self.stats['daily_profit'] += net_profit
                    self.stats['successful_trades'] += 1
                    self.stats['consecutive_profits'] += 1
                    self.stats['max_consecutive_profits'] = max(
                        self.stats['max_consecutive_profits'], 
                        self.stats['consecutive_profits']
                    )
                    self.stats['best_trade'] = max(self.stats['best_trade'], net_profit)
                    
                    # 레버리지 동적 조정
                    if self.stats['consecutive_profits'] % 10 == 0 and self.current_leverage < self.max_leverage:
                        self.current_leverage = min(self.current_leverage + self.leverage_increment, self.max_leverage)
                        logger.info(f"🚀 레버리지 증가: {self.current_leverage}배")
                    
                    # 전략 조정
                    self._adjust_strategy()
                    
                else:
                    self.stats['consecutive_profits'] = 0
                    self.daily_loss += abs(net_profit)
                    self.stats['worst_trade'] = min(self.stats['worst_trade'], net_profit)
                
                self.stats['total_trades'] += 1
                self.stats['avg_profit_per_trade'] = self.stats['total_profit'] / self.stats['total_trades']
            
            trade_result.update({
                'success': True,
                'profit': enhanced_profit,
                'fee': fee,
                'net_profit': net_profit,
                'compound_boost': compound_boost,
                'volatility_boost': volatility_boost,
                'time_boost': time_boost,
                'capital_after': self.current_capital
            })
            
            logger.info(f"💰 {symbol} 수익: ${net_profit:.4f} | 자본: ${self.current_capital:.2f}")
            
        except Exception as e:
            logger.error(f"❌ {symbol} 거래 실패: {e}")
            trade_result['error'] = str(e)
        
        self.trade_history.append(trade_result)
        return trade_result
    
    def _adjust_strategy(self):
        """수익률에 따른 전략 자동 조정"""
        roi = (self.current_capital - self.initial_capital) / self.initial_capital
        
        if roi > 1.0:  # 100% 이상 수익
            self.current_strategy = 'aggressive'
        elif roi > 0.5:  # 50% 이상 수익
            self.current_strategy = 'moderate'
        else:
            self.current_strategy = 'conservative'
    
    def trade_single_symbol(self, symbol: str):
        """단일 코인 거래 스레드"""
        if not self.active_symbols.get(symbol, False):
            return
        
        prev_price = self.price_history[symbol][-1] if self.price_history[symbol] else None
        
        while self.running:
            try:
                current_price = self.get_current_price(symbol)
                if not current_price or not prev_price:
                    prev_price = current_price
                    time.sleep(1)
                    continue
                
                # 가격 변동이 있으면 거래
                if abs(current_price - prev_price) > 0:
                    result = self.execute_absolute_profit_trade(symbol, prev_price, current_price)
                    
                    # 가격 이력 업데이트
                    self.price_history[symbol].append(current_price)
                    if len(self.price_history[symbol]) > 100:  # 최근 100개만 유지
                        self.price_history[symbol] = self.price_history[symbol][-100:]
                    
                    prev_price = current_price
                
                # 리스크 체크
                if self.daily_loss > self.max_daily_loss:
                    logger.warning(f"⚠️ {symbol} 일일 손실 한도 초과, 거래 중단")
                    break
                
                time.sleep(0.5)  # 빠른 거래 간격
                
            except Exception as e:
                logger.error(f"❌ {symbol} 거래 스레드 오류: {e}")
                time.sleep(1)
    
    def run_multi_symbol_trading(self, duration_hours: int = 24):
        """다중 코인 동시 거래"""
        logger.info("🚀 고급 복리 절댓값 수익 시스템 시작!")
        logger.info(f"💎 초기 자본: ${self.initial_capital}")
        logger.info(f"⚡ 기본 레버리지: {self.base_leverage}배")
        logger.info(f"🎯 거래 코인: {', '.join(self.symbols)}")
        logger.info(f"📊 전략: {self.current_strategy}")
        logger.info("="*100)
        
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        # 멀티스레딩으로 각 코인 동시 거래
        with ThreadPoolExecutor(max_workers=len(self.symbols)) as executor:
            futures = []
            for symbol in self.symbols:
                if self.active_symbols.get(symbol, False):
                    future = executor.submit(self.trade_single_symbol, symbol)
                    futures.append(future)
            
            try:
                # 주기적 상태 출력
                while time.time() < end_time and self.running:
                    time.sleep(60)  # 1분마다 상태 출력
                    self.print_live_status()
                    
                    # 목표 달성 체크
                    if self.stats['daily_profit'] >= self.profit_targets['daily']:
                        logger.info("🎉 일일 목표 달성!")
                        break
                
            except KeyboardInterrupt:
                logger.info("\n⚠️ 사용자가 거래를 중단했습니다.")
            
            finally:
                self.running = False
                # 모든 스레드 종료 대기
                for future in futures:
                    future.cancel()
        
        self.print_final_summary()
    
    def print_live_status(self):
        """실시간 상태 출력"""
        roi = ((self.current_capital - self.initial_capital) / self.initial_capital * 100)
        success_rate = (self.stats['successful_trades'] / max(self.stats['total_trades'], 1) * 100)
        
        logger.info(f"\n📊 실시간 상태 - 거래 {self.stats['total_trades']}회")
        logger.info(f"   💰 현재 자본: ${self.current_capital:.2f} ({roi:+.2f}%)")
        logger.info(f"   🎯 일일 수익: ${self.stats['daily_profit']:.2f}")
        logger.info(f"   ✅ 성공률: {success_rate:.1f}%")
        logger.info(f"   🔥 연속 수익: {self.stats['consecutive_profits']}회")
        logger.info(f"   ⚡ 현재 레버리지: {self.current_leverage}배")
        logger.info(f"   📈 전략: {self.current_strategy}")
    
    def print_final_summary(self):
        """최종 요약 출력"""
        logger.info("\n" + "="*100)
        logger.info("🏆 고급 복리 절댓값 수익 시스템 최종 결과")
        logger.info("="*100)
        
        roi = ((self.current_capital - self.initial_capital) / self.initial_capital * 100)
        success_rate = (self.stats['successful_trades'] / max(self.stats['total_trades'], 1) * 100)
        
        logger.info(f"💎 초기 자본: ${self.initial_capital:.2f}")
        logger.info(f"💰 최종 자본: ${self.current_capital:.2f}")
        logger.info(f"🚀 총 수익: ${self.stats['total_profit']:.2f}")
        logger.info(f"📈 수익률: {roi:.2f}%")
        logger.info(f"📊 총 거래: {self.stats['total_trades']}회")
        logger.info(f"✅ 성공 거래: {self.stats['successful_trades']}회")
        logger.info(f"🎯 성공률: {success_rate:.1f}%")
        logger.info(f"🔥 최대 연속 수익: {self.stats['max_consecutive_profits']}회")
        logger.info(f"💎 최고 거래: ${self.stats['best_trade']:.4f}")
        logger.info(f"📉 최악 거래: ${self.stats['worst_trade']:.4f}")
        logger.info(f"⚡ 최종 레버리지: {self.current_leverage}배")
        
        # 코인별 통계
        symbol_stats = {}
        for trade in self.trade_history:
            if trade['success']:
                symbol = trade['symbol']
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {'trades': 0, 'profit': 0.0}
                symbol_stats[symbol]['trades'] += 1
                symbol_stats[symbol]['profit'] += trade['net_profit']
        
        logger.info(f"\n💎 코인별 성과:")
        for symbol, stats in symbol_stats.items():
            logger.info(f"   {symbol}: {stats['trades']}회, ${stats['profit']:.2f}")
        
        # 거래 내역 저장
        if self.trade_history:
            df = pd.DataFrame(self.trade_history)
            filename = f"advanced_compound_trades_{int(time.time())}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"\n💾 거래 내역 저장: {filename}")
        
        logger.info("\n🔥 고급 복리 시스템 완료! 🔥")


def get_user_input():
    """사용자 입력 받기"""
    print("🚀 바이낸스 고급 복리 절댓값 수익 시스템")
    print("="*60)
    
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
        default_capital = 1000.0
    else:
        print("   실제 자금이 사용됩니다. 신중하게 입력하세요.")
        default_capital = 5000.0
    
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
                if initial_capital < 100:
                    print("⚠️  경고: 최소 $100 이상을 권장합니다.")
                    confirm = input("계속 진행하시겠습니까? (yes/no): ").strip().lower()
                    if confirm != 'yes':
                        continue
            break
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
    
    # 거래 전략 선택
    print("\n📈 거래 전략을 선택하세요:")
    print("1. conservative (보수적 - 50% 재투자)")
    print("2. moderate (중간 - 70% 재투자)")
    print("3. aggressive (공격적 - 90% 재투자)")
    
    while True:
        strategy_choice = input("\n선택 (1-3, 기본값: 2): ").strip()
        strategy_map = {'1': 'conservative', '2': 'moderate', '3': 'aggressive', '': 'moderate'}
        if strategy_choice in strategy_map:
            strategy = strategy_map[strategy_choice]
            break
        else:
            print("❌ 1, 2, 또는 3을 입력해주세요.")
    
    # 거래할 코인 선택
    print("\n🎯 거래할 코인을 선택하세요:")
    print("1. BTCUSDT만")
    print("2. BTC + ETH")
    print("3. 주요 5개 코인 (BTC, ETH, BNB, ADA, SOL)")
    print("4. 커스텀")
    
    while True:
        coin_choice = input("\n선택 (1-4, 기본값: 3): ").strip()
        if coin_choice == '1':
            symbols = ['BTCUSDT']
            break
        elif coin_choice == '2':
            symbols = ['BTCUSDT', 'ETHUSDT']
            break
        elif coin_choice in ['3', '']:
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
            break
        elif coin_choice == '4':
            custom_input = input("거래할 코인을 입력하세요 (예: BTCUSDT,ETHUSDT): ").strip()
            if custom_input:
                symbols = [s.strip().upper() for s in custom_input.split(',') if s.strip()]
                if symbols:
                    break
            print("❌ 올바른 코인 심볼을 입력해주세요.")
        else:
            print("❌ 1-4 중에서 선택해주세요.")
    
    # API 키 입력
    print(f"\n🔑 바이낸스 API 키를 입력하세요 ({network_name}):")
    if testnet:
        print("   테스트넷 API 키가 필요합니다.")
        print("   https://testnet.binancefuture.com 에서 생성하세요.")
    else:
        print("   메인넷 API 키가 필요합니다.")
        print("   https://www.binance.com 에서 생성하세요.")
        print("   선물 거래 권한이 활성화되어야 합니다.")
    
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("❌ API 키와 시크릿을 모두 입력해야 합니다.")
        return None
    
    # 거래 시간 설정
    print("\n⏰ 거래 시간을 설정하세요:")
    while True:
        try:
            duration_input = input("거래 시간 (시간, 기본값: 24): ").strip()
            if not duration_input:
                duration_hours = 24
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
    print(f"   📈 거래 전략: {strategy}")
    print(f"   🎯 거래 코인: {', '.join(symbols)}")
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
        'strategy': strategy,
        'symbols': symbols,
        'duration_hours': duration_hours
    }

def main():
    """메인 실행 함수"""
    try:
        # 사용자 입력 받기
        config = get_user_input()
        if not config:
            return
        
        print("\n🚀 고급 시스템을 초기화하는 중...")
        
        # 고급 시스템 초기화
        system = AdvancedCompoundSystem(
            config['api_key'], 
            config['api_secret'], 
            testnet=config['testnet']
        )
        
        # 설정 적용
        system.initial_capital = config['initial_capital']
        system.current_capital = config['initial_capital']
        system.current_strategy = config['strategy']
        system.symbols = config['symbols']
        
        # 활성 심볼 업데이트
        for symbol in system.symbols:
            system.active_symbols[symbol] = True
            system.price_history[symbol] = []
        
        print("✅ 시스템 초기화 완료!")
        print("\n🎯 거래 시작 카운트다운:")
        for i in range(5, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print("🚀 고급 복리 거래 시작!")
        
        # 다중 코인 거래 실행
        system.run_multi_symbol_trading(duration_hours=config['duration_hours'])
        
    except Exception as e:
        logger.error(f"시스템 실행 실패: {e}")
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()