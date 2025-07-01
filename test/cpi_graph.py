import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
from datetime import datetime, timedelta

# 날짜 설정 (11년간 데이터를 받아야 최근 10년의 변화율 계산 가능)
end_date = datetime.today()
start_date = end_date - timedelta(days=365 * 11)

# FRED에서 CPIAUCSL (월별 CPI 지수) 데이터 불러오기
cpi = web.DataReader('CPIAUCSL', 'fred', start_date, end_date)

# 전년 동월 대비 연간 인플레이션율 계산 (%)
cpi['YoY Inflation (%)'] = cpi['CPIAUCSL'].pct_change(periods=12) * 100

# 최근 10년 데이터만 선택
cpi_yoy = cpi.dropna().loc[end_date - timedelta(days=365*10):]

# 마지막 값
last_date = cpi_yoy.index[-1]
last_value = cpi_yoy['YoY Inflation (%)'][-1]

# 그래프 그리기
plt.figure(figsize=(12, 6))
plt.plot(cpi_yoy.index, cpi_yoy['YoY Inflation (%)'], label='CPI YoY Inflation Rate (%)', linewidth=2)
plt.scatter(last_date, last_value, color='red', zorder=5)
plt.text(last_date, last_value + 0.3, f'{last_value:.2f}%', color='red', fontsize=12)

plt.title('U.S. Consumer Price Index – Annual Inflation Rate (YoY)', fontsize=16)
plt.xlabel('Date')
plt.ylabel('Inflation Rate (%)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
