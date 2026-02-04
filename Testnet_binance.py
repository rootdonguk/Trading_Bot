# pip install python-binance matplotlib pandas numpy

from binance.client import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# =======================
# Binance Testnet 연결
# =======================
api_key = "YOUR_TESTNET_API_KEY"
api_secret = "YOUR_TESTNET_API_SECRET"

client = Client(api_key, api_secret, testnet=True)

symbol = "BTCUSDT"
initial_capital = 20  # 20달러 시작
leverage = 20
fee_rate = 0.001
n_steps = 50
sleep_sec = 1  # 가격 조회 간격

capital = initial_capital

df = pd.DataFrame({
    "step": range(n_steps),
    "price": np.zeros(n_steps),
    "profit": np.zeros(n_steps),
    "fee": np.zeros(n_steps),
    "capital_after": np.zeros(n_steps)
})

# =======================
# 시뮬레이션 루프
# =======================
for i in range(n_steps):
    # 실시간 가격 조회
    price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
    df.at[i, "price"] = price

    if i == 0:
        df.at[i, "capital_after"] = capital
        prev_price = price
        continue

    # 절댓값 기반 수익: |가격 변동| * 레버리지 * 자본
    change = abs(price - prev_price)
    profit = capital * leverage * (change / prev_price)
    fee = profit * fee_rate
    capital = capital + profit - fee

    df.at[i, "profit"] = profit
    df.at[i, "fee"] = fee
    df.at[i, "capital_after"] = capital

    prev_price = price
    time.sleep(sleep_sec)

# =======================
# 요약 출력
# =======================
summary = {
    "initial_capital": initial_capital,
    "final_capital": capital,
    "total_profit": df["profit"].sum(),
    "total_fee": df["fee"].sum(),
    "net_profit": capital - initial_capital
}

print("==== 절댓값 수익 시뮬레이션 ====")
print(summary)
print("==== 단계별 샘플 (처음 10 단계) ====")
print(df.head(10))

# =======================
# 시각화
# =======================
plt.figure(figsize=(12,6))
plt.plot(df["step"], df["capital_after"], label="Capital", color="black")
plt.scatter(df["step"], df["capital_after"], c="green")
plt.xlabel("Step")
plt.ylabel("Capital ($)")
plt.title("Absolute Value Profit Simulation (20 USDT Start, Testnet)")
plt.show()
