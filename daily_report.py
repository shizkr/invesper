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

############################################################3
# Generate an image for report
############################################################3
prompt = "Please generate an image that represents today's U.S. economy and stock market."
response = openai.images.generate(
    prompt=prompt,
    n=1,
    size="1024x1024"
)

image_url = response.data[0].url
image_data = requests.get(image_url).content

image = Image.open(BytesIO(requests.get(image_url).content))
width, height = image.size

# 중앙 30% 계산 (높이 기준)
crop_height = int(height * 0.20)
top = (height - crop_height) // 2
bottom = top + crop_height

# 좌우는 전체 유지
left = 0
right = width

# 잘라내기
cropped_img = image.crop((left, top, right, bottom))
cropped_img.save("generated_image.png")
print("image generated!")

# 🖼  Add image to PDF (make sure the image path is correct)
pdf.image("generated_image.png", x=10, y=10, w=190)  # Adjust position/size as needed
pdf.set_y(10 + crop_height * 190 / 1024 + 5)

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
pdf.multi_cell(0, 10, f"AI 투자 리포트- {today}\n", align="C")
pdf.set_font("NotoSansKR-Regular", size=11)
pdf.set_text_color(0, 0, 0)

###################################################
# AI report based on latest news from news api
###################################################
# Ask GPT for report.
pdf.set_font("NotoSansKR-Regular", size=12)
pdf.set_text_color(0, 0, 255)
pdf.multi_cell(0, 10, f"주요 뉴스 및 영향\n", align="C")
pdf.set_font("NotoSansKR-Regular", size=11)
pdf.set_text_color(0, 0, 0)

url = 'https://gnews.io/api/v4/top-headlines'
params = {
    "country": "us",
    "lang": 'kr',
    "category": "business",
    "max": 10,
    "apikey": GNEWS_API_KEY
}
response = requests.get(url, params=params)

# 응답
input_question = ''
if response.status_code == 200:
    news_data = response.json()
    articles = news_data.get('articles', [])

    pdf.set_font("NotoSansKR-Regular", style="U", size=11)
    pdf.set_text_color(0, 0, 255)
    for i, article in enumerate(articles, 1):
        text = translate_en_to_ko(article['title'])
        print(f"{i}. {text}")
        pdf.cell(0, 10, f"{i}. {text}", align="L", ln=True, link=article['url'])
        print(f"   📰 Source: {article['source']['name']}")
        print(f"   🔗 Link: {article['url']}")
        input_question = input_question + article['title'] + "\n"
else:
    print("❌ Failed to fetch news:", response.status_code)

# 마지막 정리
# 🤖 GPT-4o 호출
user_question = input_question + "\n" + "Please analyze its impact on the U.S. stock market in under 1000 characters. Please write in Korean"
print(f"{user_question}")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_question},
        {"role": "user", "content": user_question}
    ],
    temperature=0.5
)
answer = response.choices[0].message.content
pdf.set_font("NotoSansKR-Regular", size=11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 10, f"\n{answer} \n")

###################################################
# questions
###################################################
questions = ["macroeconomy_default.txt", "equity_market.txt", "asset_etf.txt", "portfolio_perspective.txt"]
for u_question in questions:
    # 파일 읽고 문자열로 합치기
    with open("questions/" + u_question, "r", encoding="utf-8") as f1, open("questions/user_mode_korean.txt", "r", encoding="utf-8") as f2:
        content1 = f1.read()
        content2 = f2.read()

    user_question = content1 + "\n" + content2  # 줄바꿈 포함하여 연결

    # 🤖 GPT-4o 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_question},
            {"role": "user", "content": user_question}
        ],
        temperature=0.5
    )

    answer = response.choices[0].message.content

    pdf.set_font("NotoSansKR-Regular", size=12)
    pdf.set_text_color(0, 0, 255)
    if u_question.startswith("macroeconomy"):
        pdf.multi_cell(0, 10, f"거시경제 분석\n", align="C")
    elif u_question.startswith("equity"):
        pdf.multi_cell(0, 10, f"주식 시장 분석\n", align="C")
    elif u_question.startswith("asset"):
        pdf.multi_cell(0, 10, f"자산 시장 및 ETF 분석\n", align="C")
    elif u_question.startswith("portfolio"):
        pdf.multi_cell(0, 10, f"포트폴리오 전략 분석\n", align="C")

    pdf.set_font("NotoSansKR-Regular", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, f"{answer} \n", align="L")

###################################################
# 보고서에 넣을 종목 리스트
###################################################
tickers = ["AAPL", "AMZN", "AVGO", "META", "MSFT", "NVDA", "GOOGL", "TSLA", "NFLX"]
etf = ["BITB", "EDV", "FLIN", "GLD", "IEF", "IEMG", "ITA", "IVV", "SCHD", "SGOV", "TLT", "TMF", "VEA", "VNQ", "XLE", "XLF", "XLP", "XLV"]

combined_symbol = ", ".join(tickers) + ", ".join(etf)
stock_question = "위의 주식 및 ETF 종목을 분석해주고, 포트폴리오를 현재 글로벌 경제 기준으로 재조정해줘. 한글로 써줘"
user_question = combined_symbol + " " + stock_question


pdf.set_text_color(0, 0, 255)
pdf.set_font("NotoSansKR-Regular", size=12)
pdf.multi_cell(0, 10, f"포트폴리오 분석 및 전망 \n", align="C")
pdf.set_font("NotoSansKR-Regular", size=11)
pdf.set_text_color(0, 0, 0)

# 마지막 정리
# 🤖 GPT-4o 호출
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_question},
        {"role": "user", "content": user_question}
    ],
    temperature=0.5
)   
answer = response.choices[0].message.content
pdf.multi_cell(0, 10, f"{answer} \n")

def get_etf_current_price(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if not data.empty:
        current_price = data["Close"].iloc[-1]
        return round(current_price, 2)
    else:
        return None

"""
pdf.set_font("NotoSansKR-Regular", size=12)
pdf.multi_cell(0, 10, f"주요 주식 및 ETF 현황 \n", align="C")
pdf.set_font("NotoSansKR-Regular", size=11)

# 각 종목에 대해 정보 수집
for symbol in tickers:
    stock = yf.Ticker(symbol)
    info = stock.info

    name = info.get("longName", symbol)
    current = info.get("currentPrice", "N/A")
    high52 = info.get("fiftyTwoWeekHigh", "N/A")
    low52 = info.get("fiftyTwoWeekLow", "N/A")
    pe = info.get("trailingPE", "N/A")
    market_cap = info.get("marketCap", "N/A")

    # 출력
    pdf.cell(200, 10, f"[{symbol}] {name}",new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("NotoSansKR-Regular", size=11)
    pdf.multi_cell(0, 8,
        f"현재가: ${current}\n"
        f"52주 최고가: ${high52} / 최저가: ${low52}\n"
        f"P/E 비율: {pe}\n"
        f"시가총액: {market_cap:,} USD"
    )
    pdf.ln(5)


# ETF 종목에 대해 정보 수집
for symbol in etf:
    stock = yf.Ticker(symbol)
    info = stock.info

    name = info.get("longName", symbol)
    current = get_etf_current_price(symbol)
    high52 = info.get("fiftyTwoWeekHigh", "N/A")
    low52 = info.get("fiftyTwoWeekLow", "N/A")
    pe = info.get("trailingPE", "N/A")

    # 출력
    pdf.cell(200, 10, f"[{symbol}] {name}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("NotoSansKR-Regular", size=11)
    pdf.multi_cell(0, 8,
        f"현재가: ${current}\n"
        f"52주 최고가: ${high52} / 최저가: ${low52}\n"
        f"P/E 비율: {pe}\n"
    )
    pdf.ln(5)
"""

filename = f"ai_invest_report_{today}.pdf"
print(filename)
pdf.output(filename)

recipients = ["invesperman@gmail.com"]
bcc_recipients = ["denny.ds.yang@gmail.com", "denny.ds.yang2@gmail.com"]

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

