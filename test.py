import os
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("telegram_client.log"), logging.StreamHandler()]
)

# 텔레그램 API 정보
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# 텔레그램 클라이언트 생성 (봇 대신 텔레그램 계정으로 로그인)
client = TelegramClient('session_name1', api_id, api_hash)

# 메시지 핸들러 (모든 채널의 메시지 수신)
@client.on(events.NewMessage())
async def handler(event):
    # 수신된 메시지 확인
    message_text = event.message.message.strip()
    chat_id = event.chat_id

    # 채널 ID와 메시지 출력 (디버깅용)
    print(f"📩 채널 ID: {chat_id}")
    print(f"📩 수신된 메시지: {message_text}")

    # 로그에도 메시지 출력
    logging.info(f"📩 채널 ID: {chat_id} - 메시지: {message_text}")

# 클라이언트 실행
async def main():
    print("🚀 클라이언트 실행 중... 메시지를 기다리는 중...")
    await client.start()  # 텔레그램 계정으로 인증
    await client.run_until_disconnected()  # 메시지 수신 대기

with client:
    client.loop.run_until_complete(main())