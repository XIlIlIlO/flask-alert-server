from flask import Flask, request, jsonify

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

# 🔥 이 부분이 꼭 필요함!
if __name__ == '__main__':
    app.run(port=5000, debug=True)
