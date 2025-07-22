from flask import Flask, request
import os
import requests

app = Flask(__name__)

messages_by_channel = {
    '-1002438287858': [],
    '-1002751858885': [],
    '-1002408933093': []
}

latest_photo_by_channel = {}  # 채널별 최근 이미지 file_id 저장

BOT_TOKEN = "8015725286:AAHPS-Uh7-KGp7F3WxxZrEQFE_hh1Mp663o"
TELEGRAM_FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

def get_file_url(file_id):
    file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
    file_path = file_info['result']['file_path']
    return TELEGRAM_FILE_URL + file_path

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    post = data.get('channel_post', {})
    chat_id = str(post.get('chat', {}).get('id', ''))

    # 텍스트 저장
    text = post.get('text', '')
    if text and chat_id in messages_by_channel:
        print(f"📩 채널 {chat_id}:", text)
        messages_by_channel[chat_id].append(text)
        if len(messages_by_channel[chat_id]) > 10:
            messages_by_channel[chat_id].pop(0)

    # 이미지 저장
    photos = post.get('photo', [])
    if photos and chat_id in messages_by_channel:
        highest_res_photo = photos[-1]
        file_id = highest_res_photo.get('file_id')
        if file_id:
            latest_photo_by_channel[chat_id] = file_id
            print(f"🖼 채널 {chat_id}의 새 이미지 등록됨.")

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
                text-shadow: none;
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
                text-shadow: none;
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


@app.route('/images/<channel_id>')
def images_html(channel_id):
    file_id = latest_photo_by_channel.get(channel_id)

    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="30">
        <style>
            body {
                background-color: #000;
                text-align: center;
                margin: 0;
                padding: 30px;
            }
            img {
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 0 15px #00f0ff;
            }
            p {
                color: #888;
                font-size: 18px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
    """

    if file_id:
        image_url = get_file_url(file_id)
        html += f'<img src="{image_url}" alt="최근 이미지">'
    else:
        html += "<p>📭 아직 등록된 이미지가 없습니다.</p>"

    html += "</body></html>"
    return html


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
