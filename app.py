import streamlit as st

st.title("📊 나의 첫 Streamlit 앱")
st.write("여기는 대시보드입니다.")

number = st.slider("숫자를 선택하세요", 0, 100)
st.write(f"선택한 숫자: {number}")
