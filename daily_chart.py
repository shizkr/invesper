import random
import os
import openai
from openai import OpenAI
from fpdf import FPDF
import yagmail
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
from fpdf.enums import XPos, YPos
import requests
import textwrap
from PIL import Image
from io import BytesIO
from deep_translator import GoogleTranslator

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다

# 환경 변수 로드 (GitHub Actions에서는 Secrets로 자동 주입됨)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GNEWS_API_KEY = os.environ["GNEWS_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

# OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# 📝 PDF 생성
pdf = FPDF()
pdf.add_page()

act_width = pdf.w - pdf.l_margin - pdf.r_margin

pdf.add_font("NotoSansKR-Regular", "", "fonts/static/NotoSansKR-Regular.ttf")
pdf.add_font("NotoSansKR-Bold", "", "fonts/static/NotoSansKR-Bold.ttf")
pdf.set_font("NotoSansKR-Regular", size=11)

# 오늘 날짜
today = datetime.today().strftime("%Y-%m-%d")

def translate_en_to_ko(text):
    return GoogleTranslator(source='en', target='ko').translate(text)

# system question
filename = "questions/system_default.txt"
with open(filename, 'r', encoding='utf-8') as file:
    system_question = file.read()

###################################################
# Title
###################################################
pdf.set_font("NotoSansKR-Bold", size=16)
pdf.set_text_color(0, 0, 255)
pdf.multi_cell(0, 10, f"미국 경제 지표 Chart - {today}\n", align="C")
pdf.set_font("NotoSansKR-Regular", size=11)
pdf.set_text_color(0, 0, 0)

###################################################
# SP500 chart
###################################################
import matplotlib.pyplot as plt
from PyPDF2 import PdfMerger

# S&P 500 데이터 불러오기
sp500 = yf.Ticker("^GSPC")
data = sp500.history(period="5y")

# 최신 날짜와 가격
last_date = data.index[-1]
last_price = data['Close'].iloc[-1]

# 그래프 그리기
plt.figure(figsize=(12, 6))
plt.plot(data['Close'], label='S&P 500', linewidth=2)
plt.title('S&P 500 Index')
plt.xlabel('Date')
plt.ylabel('Closing Price')
plt.legend()
plt.grid(True)

plt.text(last_date, last_price, f'{last_price:.2f}', color='red', fontsize=12,
         verticalalignment='bottom', horizontalalignment='right')
value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

pdf.image(image_name, x=10, y=pdf.get_y(), w=act_width)
start_y = pdf.get_y()

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)
os.remove(image_name)

# Find next pdf starting point
start_y += 5 + scaled_height

###################################################
# unemployeement chart
###################################################
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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = int(start_y) + int(scaled_height)  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# CPI rate chart 
###################################################
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
last_value = cpi_yoy['YoY Inflation (%)'].iloc[-1]

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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = int(start_y) + int(scaled_height)  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page() 
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
print(start_y) # next start point

os.remove(image_name)

###################################################
# 10Y US BOND chart 
###################################################
today = datetime.today().strftime('%Y-%m-%d')
start = '2015-01-01'

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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)
print("scaled heigh")
print(start_y)
print(scaled_height)

# Find next pdf starting point
start_next = int(start_y) + int(scaled_height)  # end of current image
print("start_next US 1-Y")
print(start_next) # next start point
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# SP 500 PE chart 
###################################################
import pandas as pd
from bs4 import BeautifulSoup

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

image_name = "chart_" + f'{start_y}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# VIX index chart last 2 year 
###################################################
print("VIX index")
# VIX 지수 데이터 다운로드
vix = yf.Ticker("^VIX")
hist = vix.history(period="2y")  # 최근 2년 데이터

# 마지막 값 추출
last_date = hist.index[-1]
last_close = hist['Close'].iloc[-1]

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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# FED Interest rate chart 
###################################################
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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# Gold price chart 
###################################################
# Fetch historical data for gold price
symbol = "GC=F"  # Gold Futures symbol on Yahoo Finance
gold_data = yf.download(symbol, start="1975-01-01", end=datetime.now().strftime("%Y-%m-%d"))

# Reset index for easier handling
gold_data.reset_index(inplace=True)

# Plotting the gold price
plt.figure(figsize=(12, 6))
plt.plot(gold_data['Date'], gold_data['Close'], label='Gold Price')
plt.title('Gold Price')
plt.xlabel('Date')
plt.ylabel('Price (USD per ounce)')
plt.grid(True)
plt.legend()

# Highlighting the latest value
last_date = pd.Timestamp(gold_data['Date'].iloc[-1])  # Ensure proper date formatting
last_price = float(gold_data['Close'].iloc[-1])  # Ensure scalar float value for formatting
plt.scatter(last_date, last_price, color='red', zorder=5)
plt.text(
    last_date, last_price,
    f"${last_price:.2f}\n{last_date.strftime('%Y-%m-%d')}",
    fontsize=10, color='red', va='bottom', ha='right',
    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3')
)

plt.tight_layout()

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# US 10-Year minus 2-Year Treasury Yield Spread 
###################################################
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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# CNN FEAR GREEDY INDEX graph 
###################################################
image_name = 'cnn_fear_greed_chart.png'

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
#os.remove(image_name)

###################################################
# Dollar Index 
###################################################
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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)
###################################################
# US M2 chart 
###################################################
# Get last 10 years
end = datetime.today()
start = end - timedelta(days=365*10)

# Download US M2 Money Stock from FRED ("M2SL")
df = web.DataReader('M2SL', 'fred', start, end)

plt.figure(figsize=(14, 7))
plt.plot(df.index, df['M2SL'], label='US M2 Money Stock')
plt.title('US M2 Money Stock (Last 10 Years)')
plt.xlabel('Date')
plt.ylabel('Billions of Dollars')
plt.legend()
plt.grid()

# Annotate last value and date
last_date = df.index[-1].strftime('%Y-%m-%d')
last_value = df['M2SL'][-1]
plt.annotate(f"{last_value:.2f} ({last_date})",
             xy=(df.index[-1], last_value),
             xytext=(-100, 40),
             textcoords='offset points',
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=12,
             color='red',
             bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='white', alpha=0.8))

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)
###################################################
# GDP Growth Rate 
###################################################
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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size 
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)

###################################################
# US PPI YoY Last 10 Y 
###################################################
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

value = random.randint(1, 1000)
image_name = "chart_" + f'{value}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size 
scaled_height = act_width * (height_px / width_px)

# Find next pdf starting point
start_next = start_y + scaled_height  # end of current image
if start_next > pdf.h - pdf.b_margin:
    pdf.add_page()
    #print("new page")
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=act_width)
start_y += 5 + scaled_height
#print(start_y) # next start point
os.remove(image_name)
###################################################
# Save to pdf file
###################################################
filename = f"economy_chart_report_{today}.pdf"
print(filename)
pdf.output(filename)

