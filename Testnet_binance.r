# 패키지 설치
install.packages(c("httr", "jsonlite", "ggplot2", "dplyr"))
library(httr)
library(jsonlite)
library(ggplot2)
library(dplyr)

# =======================
# Binance Testnet API
# =======================
api_key <- "YOUR_TESTNET_API_KEY"
api_secret <- "YOUR_TESTNET_API_SECRET"
base_url <- "https://testnet.binancefuture.com/fapi/v1/ticker/price"

symbol <- "BTCUSDT"
initial_capital <- 0.3
leverage <- 20
fee_rate <- 0.001
n_steps <- 50
sleep_sec <- 1  # 가격 조회 간격 (초)

df <- data.frame(
  step = 1:n_steps,
  price = numeric(n_steps),
  capital_before = numeric(n_steps),
  profit = numeric(n_steps),
  fee = numeric(n_steps),
  capital_after = numeric(n_steps),
  leverage = leverage,
  position = rep("LONG", n_steps)
)

df$capital_before[1] <- initial_capital
df$capital_after[1] <- initial_capital

capital <- initial_capital

# =======================
# 시뮬레이션 루프
# =======================
for(i in 1:n_steps){
  # 실시간 가격 조회
  res <- GET(base_url, query = list(symbol = symbol))
  price <- as.numeric(fromJSON(content(res, "text"))$price)
  
  df$price[i] <- price
  
  if(i == 1){
    df$capital_before[i] <- capital
    df$capital_after[i] <- capital
    df$position[i] <- "LONG"
    next
  }
  
  prev_capital <- df$capital_after[i-1]
  df$capital_before[i] <- prev_capital
  
  # 시뮬레이션 가격 변동률 (실전: 실제 전략 적용)
  change_pct <- (price - df$price[i-1]) / df$price[i-1]
  
  position <- ifelse(change_pct >= 0, "LONG", "SHORT")
  df$position[i] <- position
  
  # 수익 계산
  profit <- prev_capital * leverage * change_pct
  fee <- abs(profit) * fee_rate
  capital_new <- prev_capital + profit - fee
  
  df$profit[i] <- profit
  df$fee[i] <- fee
  df$capital_after[i] <- capital_new
  
  Sys.sleep(sleep_sec)  # 가격 반영 시간
}

# =======================
# 요약
# =======================
summary_df <- df %>%
  summarise(
    initial_capital = first(capital_before),
    final_capital = last(capital_after),
    max_capital = max(capital_after),
    min_capital = min(capital_after),
    total_profit = sum(profit),
    total_fee = sum(fee),
    net_profit = last(capital_after) - first(capital_before)
  )

print("==== 전체 시뮬레이션 요약 ====")
print(summary_df)
print("==== 단계별 샘플 (처음 10 단계) ====")
print(df[1:10, ])

# =======================
# 그래프 시각화
# =======================
ggplot(df, aes(x = step, y = capital_after, color = position)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  scale_color_manual(values = c("LONG" = "blue", "SHORT" = "red")) +
  labs(
    title = paste0(symbol, " Testnet Margin Simulation"),
    x = "Step",
    y = "Capital ($)",
    color = "Position"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, face = "bold", size = 16))
