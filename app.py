import streamlit as st
import requests
import datetime
import yfinance as yf
import openai

st.title("📈 AI 투자 예측 대시보드")
st.write("여기는 대시보드입니다.")

number = st.slider("숫자를 선택하세요", 0, 100)
st.write(f"선택한 숫자: {number}")


ticker = st.text_input("티커 입력", "AAPL")
days = st.slider("예측 일수", 1, 30)

if st.button("예측 요청"):
    response = requests.post("http://127.0.0.1:8000/predict", json={"ticker": ticker, "days": days})
    prediction = response.json()["prediction"]
    st.success(f"{days}일 후 예측 수익률: {prediction * 100:.2f}%")

# 기간 선택
start_date = st.date_input("조회 시작일", datetime.date(2023, 1, 1))
end_date = st.date_input("조회 종료일", datetime.date.today())

# 데이터 불러오기
nvda = yf.Ticker("NVDA")
data = nvda.history(start=start_date, end=end_date)

# 주가 차트 출력
st.subheader("📈 종가 (Close) 차트")
st.line_chart(data["Close"])

# 기본 정보 출력
st.subheader("🏢 기업 개요")
info = nvda.info
st.write(f"**회사명:** {info.get('longName')}")
st.write(f"**섹터:** {info.get('sector')}")
st.write(f"**시가총액:** {info.get('marketCap'):,}")
st.write(f"**PE Ratio (TTM):** {info.get('trailingPE')}")
st.write(f"**주당 순이익 (EPS):** {info.get('trailingEps')}")

# 최근 배당금
st.subheader("💰 최근 배당금 내역")
st.dataframe(nvda.dividends.tail())

# Raw 데이터 확인
with st.expander("📂 원본 데이터 보기"):
    st.dataframe(data.tail())

## Chat GPT
# 🔐 API 키 입력 (보안용 secrets.toml에서 가져오기 권장)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 👉 대체 방법: 직접 입력 (테스트용)
# openai.api_key = "sk-..."

st.title("🧠 GPT-4o ChatBot")
st.write("OpenAI의 GPT-4o 모델과 대화해보세요!")
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # 또는 직접 키 입력

# 사용자 입력
user_input = st.text_input("✍️ 궁금한 것을 입력하세요:")

default_prompt = """
당신은 고급 투자 분석 AI입니다. 다음 규칙을 따르세요:

1. 사용자가 입력한 종목의 투자 정보를 요약합니다.
2. 다음과 같은 구조로 답변하세요:
   📌 요약  
   📈 최근 시세 및 기술적 분석  
   💡 투자 포인트와 주의점  
3. 모든 답변은 한국어로 작성하고, 종목명은 영어로 유지하세요.
"""

system_prompt = st.text_area("🧠 시스템 프롬프트 (기본 설정)", value=default_prompt, height=200)

# 응답 출력
if user_input:
    with st.spinner("GPT-4o가 생각 중이에요..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "친절한 투자 비서입니다."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        st.success(reply)
