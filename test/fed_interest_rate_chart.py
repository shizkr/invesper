import pandas as pd
import matplotlib.pyplot as plt

# FRED (Federal Reserve Economic Data)에서 연방기금금리(Upper Target Rate) 데이터 다운로드
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFEDTARU"
df = pd.read_csv(url)
print(df.columns)  # 실제 컬럼명 확인

# 컬럼명 정정 예시
if 'OBSERVATION_DATE' not in df.columns:
    df.columns = [col.strip().upper() for col in df.columns]
print(df.columns)  # 다시 확인

# 날짜 변환 및 최근 50년 필터링
df['DATE'] = pd.to_datetime(df['OBSERVATION_DATE'])
df = df.dropna(subset=["DFEDTARU"])
start_date = df['DATE'].max() - pd.DateOffset(years=50)
df_50y = df[df['DATE'] >= start_date]

plt.figure(figsize=(12,6))
plt.plot(df_50y['DATE'], df_50y['DFEDTARU'], label='Federal Funds Target Rate (Upper Bound)')
plt.title('US Federal Funds Target Rate (Upper Bound)')
plt.xlabel('Date')
plt.ylabel('Interest Rate (%)')
plt.grid(True)
plt.legend()

# 최신 값 표시
last_date = df_50y['DATE'].iloc[-1]
last_rate = df_50y['DFEDTARU'].iloc[-1]
plt.scatter(last_date, last_rate, color='red', zorder=5)
plt.text(
    last_date, last_rate,
    f"{last_rate:.2f}%\n{last_date.strftime('%Y-%m-%d')}",
    fontsize=10, color='red', va='bottom', ha='right',
    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3')
)

plt.tight_layout()
plt.show()
