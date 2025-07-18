from flask import Flask, request
import os

app = Flask(__name__)

messages_by_channel = {
    '-1002438287858': [],
    '-1002751858885': [],
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
    channel_names = {
        '-1002438287858': 'SUPERHERO BINANCE 5/15/60MIN CRYPTO AI',
        '-1002751858885': '📈 SuperHero Pumping↑ & Dumping↓ AI',
        '-1002408933093': 'SUPERHERO BINANCE 1MIN SCALPING AI'
    }

    display_name = channel_names.get(channel_id, f'채널 {channel_id}')

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="1">
        <style>
            body {{
                font-family: 'Courier New', monospace;
                padding: 20px;
                background-color: #000;
                color: #fff;
                text-align: left;
            }}
            h2 {{
                color: #00f0ff;
                text-align: center;
                text-shadow: 0 0 1px #00f0ff, 0 0 10px #00f0ff, 0 0 20px #00f0ff;
            }}
            pre {{
                background: #111;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px #00f0ff, 0 0 20px #00f0ff;
                white-space: pre-wrap;
                word-break: break-word;
                font-size: 16px;
                line-height: 1.5;
                color: #fff;
                text-shadow: 0 0 1px #fff, 0 0 10px #fff;
                overflow: hidden;
            }}
        </style>
    </head>
    <body>
        <h2>📢 {display_name}</h2>
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
