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

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다

# 환경 변수 로드 (GitHub Actions에서는 Secrets로 자동 주입됨)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

# 📝 PDF 생성
pdf = FPDF()
pdf.add_page()

pdf.add_font("NotoSansKR-Regular", "", "fonts/static/NotoSansKR-Regular.ttf")
pdf.set_font("NotoSansKR-Regular", size=12)

# 오늘 날짜
today = datetime.today().strftime("%Y-%m-%d")

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

# 이미지 저장
#with open("generated_image.png", "wb") as f:
#    f.write(image_data)

print("image generated!")

pdf = FPDF()
pdf.add_page()

# 🖼 Add image to PDF (make sure the image path is correct)
pdf.image("generated_image.png", x=10, y=10, w=190)  # Adjust position/size as needed

# 💾 Save the PDF
pdf.output("image_report.pdf")

print("✅ PDF saved as image_report.pdf")
