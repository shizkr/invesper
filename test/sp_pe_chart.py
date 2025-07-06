import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Multpl.com에서 제공하는 CSV 다운로드 링크
url = 'https://www.multpl.com/s-p-500-pe-ratio/table/by-month'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
rows = table.find_all('tr')

last_date = ''
last_value = float(0)
data = []
month = 0
for row in rows[1:]:
    cols = row.find_all('td')
    if len(cols) == 2 and month < 120: # 10 years
        date = cols[0].text.strip()
        date = date[:-1] if isinstance(date, str) and not date[-1].isdigit() else date
        month += 1
        value = cols[1].text.strip()
        value = value[1:] if isinstance(value, str) and not value[0].isdigit() else value
        value = value[1:] if isinstance(value, str) and not value[0].isdigit() else value
        if month == 1:
            last_date = date
            last_value = value
        data.insert(0, (date, value))

df = pd.DataFrame(data, columns=['Date', 'P/E Ratio'])
df = df[df['Date'].astype(str).str[-1].str.isdigit()]
df['Date'] = pd.to_datetime(df['Date'])
df['P/E Ratio'] = pd.to_numeric(df['P/E Ratio'], errors = 'coerce')

# 차트 그리기
plt.figure(figsize=(12,6))
plt.plot(df['Date'], df['P/E Ratio'])
plt.title('S&P 500 P/E Ratio (by Month)')
plt.xlabel('Date')
plt.ylabel('P/E Ratio')
plt.grid(True)
plt.xticks(df['Date'][::3], rotation=45)

# 마지막 값(최신 P/E Ratio) 빨간색으로 표시 및 표기
plt.scatter(df['Date'].iloc[-1], df['P/E Ratio'].iloc[-1], color='red', zorder=5)
plt.text(
    df['Date'].iloc[-1], 
    df['P/E Ratio'].iloc[-1], 
    f"{df['P/E Ratio'].iloc[-1]:.2f}\n{df['Date'].iloc[-1].strftime('%Y-%m-%d')}",
    fontsize=10, color='red', va='bottom', ha='right',
    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3')
)

plt.tight_layout()
plt.show()
