import os
from openai import OpenAI
from fpdf import FPDF
import yagmail
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
from fpdf.enums import XPos, YPos

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다

# 환경 변수 로드 (GitHub Actions에서는 Secrets로 자동 주입됨)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

# OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# 📝 PDF 생성
pdf = FPDF()
pdf.add_page()

pdf.add_font("NotoSansKR-Regular", "", "fonts/static/NotoSansKR-Regular.ttf")
pdf.set_font("NotoSansKR-Regular", size=12)

# 오늘 날짜
today = datetime.today().strftime("%Y-%m-%d")

# system question
filename = "questions/system_default.txt"
with open(filename, 'r', encoding='utf-8') as file:
    system_question = file.read()

# user question 
filename = "questions/user_default.txt"
with open(filename, 'r', encoding='utf-8') as file:
    user_question = file.read()

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

pdf.multi_cell(0, 10, f"날짜: {today}\n\n GPT 투자 리포트\n\n{answer} \n")

# Yahoo Finance

# 보고서에 넣을 종목 리스트
tickers = ["AAPL", "AMZN", "AVGO", "META", "MSFT", "NVDA", "GOOGL", "TSLA", "NFLX"]
etf = ["BITB", "EDV", "FLIN", "GLD", "IEF", "IEMG", "ITA", "IVV", "SCHD", "SGOV", "TLT", "TMF", "VEA", "VNQ", "XLE", "XLF", "XLP", "XLV"]

combined_symbol = ", ".join(tickers) + ", ".join(etf)
stock_question = "위의 주식 종목을 분석해주고 포트폴리오를 현재 기준으로 재 조정해줘."
user_question = combined_symbol + " " + stock_question

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
pdf.multi_cell(0, 10, f"\n{answer} \n")

def get_etf_current_price(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if not data.empty:
        current_price = data["Close"].iloc[-1]
        return round(current_price, 2)
    else:
        return None

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

filename = f"gpt_invest_report_{today}.pdf"
print(filename)
pdf.output(filename)

# 📧 이메일 전송
yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASS)
yag.send(
    to=EMAIL_USER,
    subject=f"Daily GPT 투자 리포트 ({today})",
    contents="오늘의 GPT 기반 투자 리포트를 첨부했습니다.",
    attachments=filename
)

print("이메일 전송 완료")

