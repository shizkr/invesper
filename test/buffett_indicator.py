import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. S&P 500 지수 가져오기
sp500 = yf.download('^GSPC', start='2010-01-01', auto_adjust=True)
sp500 = sp500[["Close"]].rename(columns={"Close": "SP500"})
sp500.index.name = "Date"
min_sp500_date = sp500["Date"].min()

# 2. GDP 데이터 가져오기 (FRED CSV 직접 다운로드)
gdp_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP"
gdp = pd.read_csv(gdp_url, parse_dates=["observation_date"])
gdp.columns = ["Date", "GDP"]
gdp.set_index("Date", inplace=True)
gdp = gdp[gdp['Date'] >= min_sp500_date]
gdp = gdp.resample("D").ffill()

# 3. 병합 (가장 가까운 날짜 기준)
sp500 = sp500.reset_index().sort_values("Date")
gdp = gdp.reset_index().sort_values("Date")
print(sp500)
print(gdp)
merged = pd.merge_asof(sp500, gdp, on="Date", direction="backward")
merged.set_index("Date", inplace=True)

# 4. 버핏 지수 계산
correction_factor = 1.25  # S&P500 ≈ 80% of total market
merged["Buffett Index"] = (merged["SP500"] * correction_factor / merged["GDP"]) * 100

# 5. 마지막 값 추출
last_date = merged.index[-1]
last_value = merged["Buffett Index"].iloc[-1]

# 6. 그래프 출력
plt.figure(figsize=(12, 6))
plt.plot(merged.index, merged["Buffett Index"], label="Buffett Index")
plt.axhline(y=100, color='red', linestyle='--', label='Fair Value (100%)')
plt.title("Buffett Indicator (Estimated from S&P 500 / US GDP)")
plt.ylabel("Buffett Index (%)")
plt.xlabel("Date")
plt.legend()
plt.grid(True)

# 7. 마지막 값 주석 표시
plt.annotate(f"{last_value:.2f}%\n({last_date.date()})",
             xy=(last_date, last_value),
             xytext=(-100, 30),
             textcoords="offset points",
             arrowprops=dict(arrowstyle="->"),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

plt.tight_layout()
plt.show()

print(f"📅 마지막 날짜: {last_date.date()}")
print(f"📈 Buffett Index: {last_value:.2f}%")

