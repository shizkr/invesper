import yagmail
import os
from datetime import datetime
from dotenv import load_dotenv

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]


recipients = ["invesperman@gmail.com"]

today = datetime.today().strftime("%Y-%m-%d")

file1=f"ai_invest_report_{today}.pdf"
file2=f"economy_chart_report_{today}.pdf"

# 📧 이메일 전송
yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASS)

with open("ai_invest_report_2025-07-05.html", "r", encoding="utf-8") as f:
    html_context = f.read()

html_context = "<p>오늘의 AI 투자 전망 및 경제 지표 리포트를 첨부했습니다.</p>" + html_context
yag.send(
    to="denny.ds.yang@gmail.com",
    subject=f"AI 투자와 경제 지표 리포트 ({today})",
    contents=[html_context],
    attachments=[file1]
)

print("이메일 전송 완료")


