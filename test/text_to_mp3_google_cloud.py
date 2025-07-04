from google.cloud import texttospeech

# Load your service account key
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../security/advance-symbol-407401-6cda3249d713.json"  # Change this

# Create client
client = texttospeech.TextToSpeechClient()

# Your input text
sample = '미국 전기차 시장의 가격 인하 소식은 해당 섹터의 주식에 부정적인 영향을 미칠 수 있습니다. 수요 둔화에 대한 우려가 커질 수 있으며, 이는 테슬라와 같은 주요 전기차 제조업체의 주가에 하방 압력을 가할 수 있습니다. 한편, OPEC의 산유량 증가 소식은 유가 하락을 초래할 수 있으며, 이는 에너지 섹터에 부정적 영향을 미칠 수 있습니다. 반면, 유가 하락은 항공 및 운송업종에 긍정적일 수 있습니다.  미국 독립기념일 관련 소비 증가와 Amazon의 대규모 세일은 소비재 섹터에 긍정적 영향을 줄 수 있습니다. 그러나 국제 LGBTQ+ 여행자 감소는 관광 및 호텔업에 부정적일 수 있습니다. 마지막으로, 일자리 수치의 예측 실패는 시장의 변동성을 높일 수 있으며, 투자자들은 연준의 금리 정책을 주시할 것입니다. 전반적으로, 이러한 요소들이 혼재되어 시장의 방향성을 불확실하게 만들고 있습니다.'
synthesis_input = texttospeech.SynthesisInput(text=sample)

# Voice config (Korean)
voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR",
    name="ko-KR-Wavenet-A",  # or B, C, D
)

# Audio config
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Request synthesis
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# Save the result as MP3
with open("output.mp3", "wb") as out:
    out.write(response.audio_content)

print("MP3 saved successfully!")
