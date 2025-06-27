import os
from openai import OpenAI
from fpdf import FPDF
import yagmail
from datetime import datetime
from dotenv import load_dotenv

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다

# 📌 환경 변수 로드 (GitHub Actions에서는 Secrets로 자동 주입됨)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

# 📡 OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# 📅 오늘 날짜
today = datetime.today().strftime("%Y-%m-%d")

# 🧠 질문 설정
question = """
오늘의 투자 브리핑을 요약해줘:
1. S&P500, 나스닥, 10년물 금리 동향 요약
2. NVDA, AAPL, TSLA 주가의 최근 시세 및 기술적 분석
3. 오늘의 주요 투자 관련 뉴스 3가지 요약
4. 현재 투자 시사점과 주의할 리스크 요인 1개
"""

# 🤖 GPT-4o 호출
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "당신은 투자 애널리스트입니다. 답변은 간결하고 요약 위주로 하며 한국어로 작성해주세요."},
        {"role": "user", "content": question}
    ],
    temperature=0.7
)

answer = response.choices[0].message.content

# 📝 PDF 생성
pdf = FPDF()
pdf.add_page()

#pdf.add_font("NotoSansKR", "", "fonts/NotoSansKR-VariableFont_wght.ttf", uni=True)
#NotoSansKR-Regular.ttf
pdf.add_font("NotoSansKR-Regular", "", "fonts/static/NotoSansKR-Regular.ttf", uni=True)
pdf.set_font("NotoSansKR-Regular", size=12)

pdf.multi_cell(0, 10, f"날짜: {today}\n\n GPT 투자 리포트\n\n{answer}")

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

