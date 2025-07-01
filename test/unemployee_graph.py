import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
from datetime import datetime, timedelta

# 날짜 설정 (최근 10년)
end_date = datetime.today()
start_date = end_date - timedelta(days=365 * 10)

# FRED에서 실업률(UNRATE) 데이터 불러오기
unrate_data = web.DataReader('UNRATE', 'fred', start_date, end_date)

# 마지막 데이터 추출
last_date = unrate_data.index[-1]
last_value = unrate_data.iloc[-1, 0]

# 그래프 그리기
plt.figure(figsize=(12, 6))
plt.plot(unrate_data.index, unrate_data['UNRATE'], label='Unemployment Rate (%)', linewidth=2)
plt.scatter(last_date, last_value, color='red', zorder=5)
plt.text(last_date, last_value + 0.2, f'{last_value:.1f}%', color='red', fontsize=12)

plt.title('US unemplyeement (Last 10 year)', fontsize=16)
plt.xlabel('Date')
plt.ylabel('Unemployeement (%)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
