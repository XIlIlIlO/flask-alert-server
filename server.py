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

@app.route('/messages.html')
def messages_html():
    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="1">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
            h2 { color: #0078FF; }
            .msg { font-size: 20px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h2>📢 실시간 공지사항</h2>
    """
    if messages:
        html += f'<div class="msg">{messages[-1]}</div>'
    else:
        html += '<div class="msg">아직 등록된 메시지가 없습니다.</div>'
    html += """
    </body>
    </html>
    """
    return html


# ✅ 이건 제일 아래
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
