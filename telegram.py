import re
import os
import requests
import logging
from telethon import TelegramClient, events
import deepl  # DeepL 번역기 라이브러리
from dotenv import load_dotenv
import asyncio
import sys

if sys.platform == 'darwin':
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# 🔹 환경 변수 로드
load_dotenv(dotenv_path='/Users/sonjuwon/Desktop/python workplace/.env')

# 🔹 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("telegram_bot.log"), logging.StreamHandler()]
)

# 🔹 텔레그램 API 정보 (환경 변수에서 로드)
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# 🔹 DeepL API 설정
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(DEEPL_API_KEY)  # DeepL 번역기 초기화

# 🔹 LINE Bot API 설정
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")  # 메시지를 받을 사용자의 LINE ID

# 🔹 모니터링할 텔레그램 채널 ID 
MONITOR_CHANNELS = [-1001219894832, -1001386345244, -1001363666182, -1001606488817]

# 🔹 필터링할 키워드
FILTER_KEYWORDS = ["코인", "체인", "거래", "입출금", "코인" , "마켓추가", "거래지원"]
FILTER_KEYWORDS = [keyword.lower().replace(" ", "") for keyword in FILTER_KEYWORDS]

# 🔹 URL 제거 여부 설정
REMOVE_URLS = False  # True로 설정하면 메시지에서 URL을 제거함

# 🔹 텔레그램 클라이언트 생성
client = TelegramClient('session_name', api_id, api_hash)

# 🔹 LINE 메시지 전송 함수 (재시도 포함)
def send_line_alert(message, retry_count=3):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }

    for attempt in range(retry_count):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info(f"📩 LINE 메시지 전송 성공: {message}")
                return
            else:
                logging.warning(f"⚠️ LINE 메시지 전송 실패 (시도 {attempt + 1}/{retry_count}): {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"❌ LINE API 요청 오류 (시도 {attempt + 1}/{retry_count}): {e}")

# 🔹 메시지 정리 함수
def format_message(text):
    if REMOVE_URLS:
        text = re.sub(r'https?://\S+', '', text)  # URL 패턴 제거
    text = re.sub(r'([.!?])', r'\1\n', text)  # 문장 끝에서 개행 추가
    text = re.sub(r'\s+', ' ', text).strip()  # 연속된 공백 제거
    return text

# 🔹 메시지 핸들러 (필터링 + 번역 + LINE 전송)
@client.on(events.NewMessage(chats=MONITOR_CHANNELS))
async def handler(event):
    message_text = event.message.message.strip()
    formatted_text = format_message(message_text)

    # 📌 원본 메시지 출력 (디버깅용)
    logging.info(f"📩 수신된 메시지: {formatted_text}")

    # 키워드 필터링
    if any(keyword in formatted_text.lower().replace(" ", "") for keyword in FILTER_KEYWORDS):
        logging.info(f"✅ 필터링됨 - 메시지: {formatted_text}")

        # DeepL 번역 실행
        try:
            translated_text = translator.translate_text(formatted_text, source_lang="KO", target_lang="ZH")
            translated_message = translated_text.text
            logging.info(f"📜 번역된 메시지: {translated_message}")
        except Exception as e:
            logging.error(f"⚠️ 번역 오류: {e}")
            translated_message = "번역 실패"

        # 📢 LINE으로 메시지 전송
        alert_message = f"📢 긴급 알림!\n\n🔹 원본: {formatted_text}\n🔹 번역: {translated_message}"
        send_line_alert(alert_message)
    else:
        logging.info("❌ 필터링되지 않음")

# 🔹 클라이언트 실행
async def main():
    logging.info("🚀 클라이언트 실행 중... 메시지를 기다리는 중...")
    
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())