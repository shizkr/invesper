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

# S&P 500 데이터 다운로드
sp500 = yf.download('^GSPC', start='2020-01-01', end='2025-06-30')

# 그래프 그리기
plt.figure(figsize=(12, 6))
plt.plot(sp500['Close'], label='S&P 500', linewidth=2)
plt.title('S&P 500 Index (2020–2025)')
plt.xlabel('Date')
plt.ylabel('Closing Price')
plt.legend()
plt.grid(True)

# PDF로 저장
plt.savefig('sp500_chart.pdf', format='pdf')
