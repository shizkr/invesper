import os
import requests
import openai
from dotenv import load_dotenv
from openai import OpenAI

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()  # 로컬 환경일 경우에만 .env 파일을 불러옵니다

def send_message_to_telegram(bot_token, chat_id, message):
    """
    Sends a message to a Telegram chat.
    
    :param bot_token: Token for your Telegram bot obtained from BotFather.
    :param chat_id: The chat ID or user ID to send the message to.
    :param message: The message text to send.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.status_code}")
        print(response.json())

