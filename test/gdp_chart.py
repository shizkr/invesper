import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 10년 기간 설정
end = datetime.today()
start = end - timedelta(days=365*10)

# 미국 실질 GDP 성장률 데이터 다운로드 (분기별, 전년 동기 대비, %)
# FRED 코드: 'A191RL1Q225SBEA'
df = web.DataReader('A191RL1Q225SBEA', 'fred', start, end)

plt.figure(figsize=(14, 7))
plt.plot(df.index, df['A191RL1Q225SBEA'], marker='o', label='US Real GDP Growth Rate (YoY, %)')
plt.title('US GDP Growth (Last 10Y, YoY)')
plt.xlabel('Date')
plt.ylabel('Growth (%)')
plt.legend()
plt.grid()

# 마지막 값과 날짜 표시
last_date = df.index[-1].strftime('%Y-%m-%d')
last_value = df['A191RL1Q225SBEA'][-1]
plt.annotate(f"{last_value:.2f}% ({last_date})",
             xy=(df.index[-1], last_value),
             xytext=(-100, 30),
             textcoords='offset points',
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=12,
             color='red',
             bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='white', alpha=0.8))

plt.show()
