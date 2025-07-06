import yfinance as yf
import matplotlib.pyplot as plt

# VIX 지수 데이터 다운로드
vix = yf.Ticker("^VIX")
hist = vix.history(period="2y")  # 최근 2년 데이터

# 마지막 값 추출
last_date = hist.index[-1]
last_close = hist['Close'][-1]

plt.figure(figsize=(12, 6))
plt.plot(hist.index, hist['Close'], label='VIX Index (S&P 500 Volatility)')
plt.title('VIX (S&P 500 Volatility Index) - Last 2 Year')
plt.xlabel('Date')
plt.ylabel('VIX Index')
plt.legend()
plt.grid(True)

# 마지막 값에 마커 추가
plt.scatter(last_date, last_close, color='red', zorder=5)

# 텍스트 위치를 그래프 오른쪽 위 바깥에 표시
ax = plt.gca()
xlim = ax.get_xlim()
ylim = ax.get_ylim()

# x축 끝에서 약간 안쪽, y축 상단에서 약간 아래 위치에 텍스트 표시
text_x = hist.index[-1] + (hist.index[-1] - hist.index[0]) * 0.01
text_y = ylim[1] - (ylim[1] - ylim[0]) * 0.08

plt.text(text_x, text_y, f"{last_close:.2f}\n{last_date.date()}",
         fontsize=11, color='red', va='top', ha='left',
         bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))

plt.tight_layout()
plt.show()
