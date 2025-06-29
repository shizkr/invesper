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
NEWS_API_KEY = os.environ["NEWS_API_KEY"]

url = "https://newsapi.org/v2/top-headlines"
params = {
    "country": "us",
    "category": "business", 
    "pageSize": 10,
    "apiKey": NEWS_API_KEY
}
response = requests.get(url, params=params)
data = response.json()


def translate_en_to_ko(text):
    return GoogleTranslator(source='en', target='ko').translate(text)

print("📢 [오늘의 비즈니스 뉴스]\n")
for idx, article in enumerate(data["articles"], 1):
    print(translate_en_to_ko(article['title']))
    print(f"   🔗 {article['url']}\n")
