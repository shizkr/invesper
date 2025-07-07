import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# DXY 심볼 (Yahoo Finance 기준)
today = datetime.today().strftime('%Y-%m-%d')
dxy = yf.download('DX-Y.NYB', start='2015-07-07', end=today)

plt.figure(figsize=(14, 7))
plt.plot(dxy['Close'], label='DXY (US Dollar Index)')
plt.title('DXY (US Dollar Index) 10Y Chart')
plt.xlabel('Date')
plt.ylabel('Index')
plt.legend()
plt.grid()

# 마지막 값과 날짜 표시
last_date = dxy.index[-1].strftime('%Y-%m-%d')
last_value = float(dxy['Close'].iloc[-1])
plt.annotate(f"{last_value:.2f} ({last_date})",
             xy=(dxy.index[-1], last_value),
             xytext=(-80, 30),
             textcoords='offset points',
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=12,
             color='red',
             bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='white', alpha=0.8))

plt.show()
