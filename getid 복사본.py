import re
import os
import requests
import logging
from telethon import TelegramClient, events
import deepl
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(dotenv_path='/Users/sonjuwon/Desktop/python workplace/.env')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("telegram_bot.log"), logging.StreamHandler()]
)

# 텔레그램 API 정보
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# LINE & DeepL
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(DEEPL_API_KEY)
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")

# 모니터링할 채널
MONITOR_CHANNELS = [-1001363666182, -1001606488817]

# 필터 키워드
FILTER_KEYWORDS = ["점검", "거래", "입출금", "마켓추가", "거래지원", "유의촉구", "거래유의", "코인", "증시", "체인"]
FILTER_KEYWORDS = [k.lower().replace(" ", "") for k in FILTER_KEYWORDS]

REMOVE_URLS = True

# ✅ 개인 계정용 TelegramClient 생성 (bot_token 제거)
client = TelegramClient('my_session', api_id, api_hash).start()

# LINE 전송 함수
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
                logging.warning(f"⚠️ 전송 실패 {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"❌ LINE API 오류: {e}")

# 메시지 정리
def format_message(text):
    if REMOVE_URLS:
        text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'([.!?])', r'\1\n', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 이벤트 핸들링
@client.on(events.NewMessage(chats=MONITOR_CHANNELS))
async def handler(event):
    message_text = event.message.message.strip()
    formatted_text = format_message(message_text)

    logging.info(f"📩 수신된 메시지: {formatted_text}")
    chat_id = event.chat_id

    source = "알 수 없음"
    if chat_id == -1001363666182:
        source = "Bithumb"
    elif chat_id == -1001606488817:
        source = "Upbit"

    if any(keyword in formatted_text.lower().replace(" ", "") for keyword in FILTER_KEYWORDS):
        if "안녕하세요" in formatted_text:
            formatted_text = formatted_text.split("안녕하세요")[0].strip()
            logging.info(f"✂️ '안녕하세요' 이후 삭제됨: {formatted_text}")

        try:
            translated_text = translator.translate_text(formatted_text, source_lang="KO", target_lang="ZH-TW").text
            logging.info(f"📜 번역된 메시지: {translated_text}")
        except Exception as e:
            logging.error(f"⚠️ 번역 오류: {e}")
            translated_text = "번역 실패"

        final_message = f"{source}\n\n🔹 原文: {formatted_text}\n🔹 繁體中文: {translated_text}"
        send_line_alert(final_message)
    else:
        logging.info(f"❌ 필터링되지 않음 ({source})")

# 실행
async def main():
    logging.info("🚀 클라이언트 실행 중... 메시지를 기다리는 중...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
