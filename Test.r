install.packages("ggplot2")
install.packages("dplyr")

library(ggplot2)
library(dplyr)

initial_capital <- 100       
leverage <- 20               
fee_rate <- 0.001            
n_steps <- 200               
set.seed(42)                 

price_change <- rnorm(n_steps, mean = 0, sd = 0.01)  

df <- data.frame(
  step = 1:n_steps,
  price_change = price_change,
  capital_before = numeric(n_steps),
  profit = numeric(n_steps),
  fee = numeric(n_steps),
  capital_after = numeric(n_steps),
  leverage = leverage,
  position = rep("LONG", n_steps)
)

df$capital_before[1] <- initial_capital
df$capital_after[1] <- initial_capital

for (i in 2:n_steps) {
  prev_capital <- df$capital_after[i-1]
  df$capital_before[i] <- prev_capital
  
  profit <- price_change[i] * leverage * prev_capital
  fee <- abs(profit) * fee_rate
  capital_new <- prev_capital + profit - fee
  
  df$profit[i] <- profit
  df$fee[i] <- fee
  df$capital_after[i] <- capital_new
  
  df$position[i] <- ifelse(price_change[i] >= 0, "LONG", "SHORT")
}

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

print("==== 단계별 상세 샘플 (처음 10 단계) ====")
print(df[1:10, ])

ggplot(df, aes(x = step, y = capital_after, color = position)) +
  geom_line(size = 1) +
  geom_point(aes(color = position), size = 2) +
  scale_color_manual(values = c("LONG" = "blue", "SHORT" = "red")) +
  labs(
    title = "시뮬레이션 (LONG/SHORT 표시)",
    x = "시간 스텝",
    y = "자본($)",
    color = "포지션"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16)
  )
