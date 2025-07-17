from flask import Flask, request, jsonify
import os

app = Flask(__name__)
messages = []

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    text = data.get('channel_post', {}).get('text', '')
    if text:
        print("📩 채널 메시지 수신:", text)
        messages.append(text)
        if len(messages) > 10:
            messages.pop(0)
    return '', 200

@app.route('/messages')
def get_messages():
    return jsonify(messages=messages)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
