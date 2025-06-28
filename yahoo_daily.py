import yfinance as yf
from fpdf import FPDF
from datetime import datetime

# 보고서에 넣을 종목 리스트
tickers = ["AAPL", "AMZN", "AVGO", "META", "MSFT", "NVDA", "GOOGL", "TSLA", "NFLX"]
etf = ["BITB", "EDV", "FLIN", "GLD", "IEF", "IEMG", "ITA", "IVV", "SCHD", "SGOV", "TLT", "TMF", "VEA", "VNQ", "XLE", "XLF", "XLP", "XLV"]

# PDF 설정
pdf = FPDF()
pdf.add_page()

pdf.add_font("NotoSansKR-Regular", "", "fonts/static/NotoSansKR-Regular.ttf", uni=True)
pdf.set_font("NotoSansKR-Regular", size=12)

# 제목
today = datetime.now().strftime("%Y-%m-%d")
pdf.cell(200, 10, f"GPT 투자 리포트 - {today}", ln=True, align="C")
pdf.ln(10)

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
    pdf.cell(200, 10, f"[{symbol}] {name}", ln=True)
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
    pdf.cell(200, 10, f"[{symbol}] {name}", ln=True)
    pdf.set_font("NotoSansKR-Regular", size=11)
    pdf.multi_cell(0, 8,
        f"현재가: ${current}\n"
        f"52주 최고가: ${high52} / 최저가: ${low52}\n"
        f"P/E 비율: {pe}\n"
    )
    pdf.ln(5)
# PDF 저장
filename = f"stock_report_{today}.pdf"
pdf.output(filename)
print(f"PDF 저장 완료: {filename}")
