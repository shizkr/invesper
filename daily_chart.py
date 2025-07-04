#######
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
image_name = 'chart_sp500.png'
plt.savefig(image_name, format='png')

pdf.image(image_name, x=10, y=pdf.get_y(), w=200)
start_y = pdf.get_y()

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = 200 * (height_px / width_px)
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

image_name = "chart_" + f'{start_y}' + '.png'
plt.savefig(image_name, format='png')

pdf.image(image_name, x=10, y=start_y, w=200)

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = 200 * (height_px / width_px)
os.remove(image_name)

# Find next pdf starting point
start_y += 5 + scaled_height

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

image_name = "chart_" + f'{start_y}' + '.png'
plt.savefig(image_name, format='png')

# Find height
with Image.open(image_name) as img:
    width_px, height_px = img.size
scaled_height = 200 * (height_px / width_px)

# Find next pdf starting point
start_y += 5 + scaled_height
if start_y > pdf.h + 5 - pdf.b_margin:
    pdf.add_page() 
    pdf.set_y(pdf.t_margin)
    start_y = pdf.t_margin
pdf.image(image_name, x=10, y=start_y, w=200)
os.remove(image_name)

###################################################
# Save to pdf file
###################################################
filename = f"economy_chart_report_{today}.pdf"
print(filename)
pdf.output(filename)

recipients = ["invesperman@gmail.com"]
bcc_recipients = ["denny.ds.yang@gmail.com", "denny.ds.yang2@gmail.com"]

exit()

# 📧 이메일 전송
yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASS)
yag.send(
    to=recipients,
    bcc=bcc_recipients,
    subject=f"Daily AI 투자 리포트 ({today})",
    contents="오늘의 AI 기반 투자 리포트를 첨부했습니다.\n\n감사합니다.",
    attachments=filename
)

print("이메일 전송 완료")

