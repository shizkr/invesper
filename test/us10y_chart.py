from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt

today = datetime.today().strftime('%Y-%m-%d')
start = '2015-01-01'
start_y = start[:4]

# US10Y 데이터 다운로드
us10y = yf.download('^TNX', start=start, end=today, auto_adjust=False)

# 수익률은 /10 (퍼센트)
yields = us10y['Close']

# 그래프 그리기
plt.figure(figsize=(12, 6)) 
plt.plot(us10y.index, yields, label='US10Y Yield (%)')
plt.title('US 10-Year Treasury Yield (10Y)')
plt.xlabel('Date')
plt.ylabel('Yield (%)')
plt.grid(True)
plt.legend()

# 마지막 값 표시
last_date = us10y.index[-1].strftime('%Y-%m-%d')
last_yield = yields.iloc[-1].item()
plt.annotate(f'{last_yield:.2f}%\n({last_date})',
             xy=(us10y.index[-1], last_yield),
             xytext=(-80, 30),
             textcoords='offset points',
             arrowprops=dict(arrowstyle='->'),
             fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray"))
plt.tight_layout()
plt.show()

