from telethon.sync import TelegramClient

# 여기에 본인의 API_ID와 API_HASH 입력
API_ID = '24399221'
API_HASH = 'aa1cc5608699c374f910661db4ef11b2'

# Telethon 클라이언트 생성 및 로그인
with TelegramClient("my_session", API_ID, API_HASH) as client:
    dialogs = client.get_dialogs()  # 가입한 모든 채널, 그룹, 개인 채팅 가져오기
    
    for dialog in dialogs:
        if dialog.is_channel:  # 채널만 필터링
            print(f"채널 이름: {dialog.name}, 채널 ID: {dialog.id}")
88