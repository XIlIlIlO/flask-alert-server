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

@app.route('/messages.html')  # ✅ 반드시 app.run 위에 있어야 함
def messages_html():
    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h2 { color: #0078FF; }
            ul { list-style-type: none; padding: 0; }
            li { padding: 8px 0; border-bottom: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <h2>📢 실시간 공지사항</h2>
        <ul>
    """
    for msg in reversed(messages[-10:]):
        html += f"<li>{msg}</li>"
    html += """
        </ul>
    </body>
    </html>
    """
    return html

# ✅ 이건 제일 아래
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
