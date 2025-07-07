import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 10년 기간 설정
end = datetime.today()
start = end - timedelta(days=365*10)

# 미국 생산자 물가지수(PPI) 데이터 다운로드 (FRED 코드: 'PPIACO')
df = web.DataReader('PPIACO', 'fred', start, end)

# YoY 변화율 (%) 계산
df['PPI_YoY'] = df['PPIACO'].pct_change(periods=12) * 100

plt.figure(figsize=(14, 7))
plt.plot(df.index, df['PPI_YoY'], label='US PPI YoY Change (%)')
plt.title('US PPI YoY Rate (Last 10Y)')
plt.xlabel('Date')
plt.ylabel('Rate (%)')
plt.legend()
plt.grid()

# 마지막 값과 날짜 표시 (NaN이 아닌 마지막 값)
last_valid_index = df['PPI_YoY'].last_valid_index()
last_value = df.loc[last_valid_index, 'PPI_YoY']
last_date = last_valid_index.strftime('%Y-%m-%d')

plt.annotate(f"{last_value:.2f}% ({last_date})",
             xy=(last_valid_index, last_value),
             xytext=(-100, 30),
             textcoords='offset points',
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=12,
             color='red',
             bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='white', alpha=0.8))

plt.show()
