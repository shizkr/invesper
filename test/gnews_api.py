import os
import openai
from fpdf import FPDF
import yagmail
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
from fpdf.enums import XPos, YPos
import requests
from PIL import Image
from io import BytesIO


#
from deep_translator import GoogleTranslator
import requests

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다


######### implementation


# 환경 변수 로드 (GitHub Actions에서는 Secrets로 자동 주입됨)
GNEWS_API_KEY = os.environ["GNEWS_API_KEY"]

url = 'https://gnews.io/api/v4/top-headlines' 
params = {
    "country": "us",
    "lang": 'en',
    "category": "business", 
    "max": 10,
    "apikey": GNEWS_API_KEY
}
response = requests.get(url, params=params)

# 응답 확인
if response.status_code == 200:
    news_data = response.json()
    articles = news_data.get('articles', [])

    print("📊 Top 5 Business News:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   📰 Source: {article['source']['name']}")
        print(f"   🔗 Link: {article['url']}")
        print(f"   🕒 Published: {article['publishedAt']}\n")
else:
    print("❌ Failed to fetch news:", response.status_code)

