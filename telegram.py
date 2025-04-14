import re
import os
import requests
import logging
from telethon import TelegramClient, events
import deepl
from dotenv import load_dotenv

# 🔹 환경 변수 로드
load_dotenv(dotenv_path='/Users/sonjuwon/Desktop/python workplace/.env')

# 🔹 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("telegram_bot.log"), logging.StreamHandler()]
)

# 🔹 텔레그램 API 정보
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# 🔹 DeepL, LINE API
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(DEEPL_API_KEY)
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")

# 🔹 모니터링할 채널 ID
MONITOR_CHANNELS = [-1001219894832, -1001202540487, -1001363666182, -1001606488817, -1001386345244]

# 🔹 채널 출처 매핑
CHANNEL_SOURCE_MAP = {
    -1001219894832: "Upbit",
    -1001202540487: "Bithumb",
    -1001363666182: "블록미디어",
    -1001606488817: "블루밍비트",
    -1001386345244: "코인니스"
}

# 🔹 필터링 키워드
FILTER_KEYWORDS = ["코인", "체인", "거래", "입출금", "코인", "마켓추가", "거래지원"]
FILTER_KEYWORDS = [k.lower().replace(" ", "") for k in FILTER_KEYWORDS]

# 🔹 URL 제거 여부
REMOVE_URLS = False

# 🔹 TelegramClient 생성
client = TelegramClient('session_name', api_id, api_hash)

# 🔹 LINE 알림 전송 함수
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
                logging.warning(f"⚠️ LINE 메시지 전송 실패 ({response.status_code})")
        except requests.RequestException as e:
            logging.error(f"❌ LINE API 오류: {e}")

# 🔹 메시지 정리 함수
def format_message(text):
    if REMOVE_URLS:
        # 중간에 공백이 포함된 URL까지 제거
        text = re.sub(r'https?:\/\/(?:[\w\-]+\.)+[a-zA-Z]{2,}(?:\s*\.\s*\w+)*(?:\/[\w\-\/\.\?\=\#\&\%\~]*)?', '', text)
        # 남아있는 공백 정리
        text = re.sub(r'\s+\.\s+', '.', text)
    text = re.sub(r'([.!?])', r'\1\n', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# 🔹 메시지 핸들러
@client.on(events.NewMessage(chats=MONITOR_CHANNELS))
async def handler(event):
    message_text = event.message.message.strip()
    formatted_text = format_message(message_text)
    chat_id = event.chat_id
    source = CHANNEL_SOURCE_MAP.get(chat_id, "알 수 없음")

    logging.info(f"📌 채널 ID: {chat_id} (출처: {source})")
    logging.info(f"📩 수신된 메시지: {formatted_text}")

    if any(keyword in formatted_text.lower().replace(" ", "") for keyword in FILTER_KEYWORDS):
        logging.info(f"✅ 필터링됨 메시지")
        if "안녕하세요" in formatted_text:
            formatted_text = formatted_text.split("안녕하세요")[0].strip()
            logging.info(f"✂️ '안녕하세요' 이후 삭제됨: {formatted_text}")


        try:
            translated_text = translator.translate_text(formatted_text, source_lang="KO", target_lang="ZH-HANT").text
            logging.info(f"📜 번역 결과: {translated_text}")
        except Exception as e:
            logging.error(f"⚠️ 번역 오류: {e}")
            translated_text = "번역 실패"

        final_message = f"[{source}]\n\n🔹 原文: {formatted_text}\n🔹 中文翻譯: {translated_text}"
        send_line_alert(final_message)
    else:
        logging.info(f"❌ 필터링되지 않음 ({source})")

# 🔹 클라이언트 실행
async def main():
    logging.info("🚀 클라이언트 실행 중... 메시지를 기다리는 중...")
    await client.start()
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
