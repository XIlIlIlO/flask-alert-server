from flask import Flask, request
import os

app = Flask(__name__)

messages_by_channel = {
    '-1002438287858': [],
    '-1002673695521': [],
    '-1002408933093': []
}

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    post = data.get('channel_post', {})
    text = post.get('text', '')
    chat_id = str(post.get('chat', {}).get('id', ''))

    if text and chat_id in messages_by_channel:
        print(f"📩 채널 {chat_id}:", text)
        messages_by_channel[chat_id].append(text)
        if len(messages_by_channel[chat_id]) > 10:
            messages_by_channel[chat_id].pop(0)
    else:
        print(f"❌ 미등록 채널 또는 메시지 없음 - chat_id: {chat_id}")

    return '', 200


@app.route('/messages/<channel_id>')
def messages_html(channel_id):
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="1">
        <style>
            body {{
                font-family: 'Courier New', monospace;
                padding: 20px;
                background-color: #f9f9f9;
                text-align: left;
            }}
            h2 {{
                color: #0078FF;
                text-align: center;
            }}
            pre {{
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                white-space: pre-wrap;
                word-break: break-word;
                font-size: 14px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <h2>📢 채널 {channel_id} 공지사항</h2>
    """

    msgs = messages_by_channel.get(channel_id, [])
    if msgs:
        html += f"<pre>{msgs[-1]}</pre>"
    else:
        html += "<pre>📭 아직 등록된 메시지가 없습니다.</pre>"

    html += "</body></html>"
    return html


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
