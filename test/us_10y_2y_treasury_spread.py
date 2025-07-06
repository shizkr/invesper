import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
from matplotlib.ticker import MultipleLocator, FuncFormatter

# 1970-01-01 이후 전체 기간
start = '1970-01-01'
end = None  # 오늘까지

# FRED 데이터 다운로드
df_10y = web.DataReader('DGS10', 'fred', start, end)
df_2y = web.DataReader('DGS2', 'fred', start, end)

# 스프레드 계산
df = pd.concat([df_10y, df_2y], axis=1)
df.columns = ['10Y', '2Y']
df['Spread'] = df['10Y'] - df['2Y']

# 마지막 날짜와 값 찾기 (NaN이 아닌 값 중에서)
last_valid = df['Spread'].last_valid_index()
last_value = df.loc[last_valid, 'Spread']

# 5년 단위 x축 라벨 생성 함수
def year_format(x, pos=None):
    year = pd.to_datetime(x).year
    return f"{year}"

# 그래프 그리기
plt.figure(figsize=(16, 7))
plt.plot(df.index, df['Spread'], label='10Y - 2Y Spread')
plt.axhline(0, color='red', linestyle='--', linewidth=1)
plt.title('US 10-Year minus 2-Year Treasury Yield Spread (Since 1970)')
plt.xlabel('Date')
plt.ylabel('Yield Spread (%)')
plt.legend()
plt.grid(True)

# 5년 단위로 x축 라벨 표시
years = pd.date_range(start='1970-01-01', end=df.index[-1], freq='5YS')
plt.xticks(years, [y.year for y in years])

# 마지막 값 표시
plt.scatter(last_valid, last_value, color='orange', zorder=5)
plt.annotate(f'{last_valid.date()} : {last_value:.2f}%', 
             (last_valid, last_value), 
             textcoords="offset points", xytext=(-60,-10), ha='center',
             bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.6),
             arrowprops=dict(arrowstyle="->", color='orange'))

plt.tight_layout()
plt.show()
