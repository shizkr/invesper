import os
import openai
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
import requests

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다


######### implementation
import matplotlib.pyplot as plt

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

# PDF로 저장
plt.savefig('sp500_chart.pdf', format='pdf')
plt.show()
