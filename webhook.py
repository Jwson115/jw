from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # CORS 활성화

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 루트 경로 처리
@app.route("/")
def index():
    return "Hello, this is the webhook server!"  # 기본 페이지 내용

# 웹훅 경로
@app.route("/webhook", methods=["POST"])
def webhook():
    # 수신된 데이터 로깅
    data = request.json
    logging.info(f"📌 수신된 데이터: {data}")

    # 이벤트에서 groupId 추출
    if "events" in data:
        for event in data["events"]:
            if "source" in event and "groupId" in event["source"]:
                group_id = event["source"]["groupId"]
                logging.info(f"🔹 감지된 그룹 ID: {group_id}")
                # 추가적으로 groupId를 저장하거나 사용할 수 있습니다

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)  # 포트는 4000으로 설정
