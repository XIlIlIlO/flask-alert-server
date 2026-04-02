from flask import Flask, request
import os
import requests
import re

app = Flask(__name__)

messages_by_channel = {
    '-1002438287858': [],
    '-1002408933093': []
}

latest_photo_by_channel = {}  # 채널별 최근 이미지 file_id 저장

BOT_TOKEN = "8015725286:AAHPS-Uh7-KGp7F3WxxZrEQFE_hh1Mp663o"
TELEGRAM_FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

def get_file_url(file_id):
    file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
    file_path = file_info['result']['file_path']
    return TELEGRAM_FILE_URL + file_path

# ✅ LONG / SHORT 네온 스타일 적용
def style_trade_words(text):
    text = re.sub(
        r'\b(LONG|Long|long)\b',
        r'<span class="long-neon">\1</span>',
        text
    )
    text = re.sub(
        r'\b(SHORT|Short|short)\b',
        r'<span class="short-neon">\1</span>',
        text
    )
    return text

# ✅ 메시지 내 코인명 링크로 변환 + LONG / SHORT 색상 적용
def linkify_coin_names(text):
    lines = text.strip().split('\n')
    new_lines = []

    for line in lines:
        # ex: OMUSDT: 10.30%
        match_usdt = re.match(r'^([A-Z0-9]+USDT)\s*:\s*[\d\.]+%', line.strip())
        if match_usdt:
            symbol = match_usdt.group(1)
            url = f"https://www.binance.com/en/futures/{symbol}"
            linked = line.replace(
                symbol,
                f'<a href="{url}" target="_blank" style="color:#afff00;text-decoration:underline;">{symbol}</a>'
            )
            new_lines.append(style_trade_words(linked))
            continue

        # ex: 1. INIT   3.93% ↑ Long
        match_ranked = re.match(r'^\s*\d+\.\s+([A-Z0-9]+)\b', line)
        if match_ranked:
            coin = match_ranked.group(1)
            url = f"https://www.binance.com/en/futures/{coin}USDT"
            linked = re.sub(
                coin,
                f'<a href="{url}" target="_blank" style="color:#afff00;text-decoration:underline;">{coin}</a>',
                line,
                count=1
            )
            new_lines.append(style_trade_words(linked))
            continue

        # 통과 + LONG / SHORT 스타일 적용
        new_lines.append(style_trade_words(line))

    return '<br>'.join(new_lines)

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

    <!-- ✅ Orbitron + Gilroy 폰트 불러오기 -->
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
    <style>
        @font-face {{
            font-family: 'Gilroy';
            src: url('https://cdn.jsdelivr.net/gh/xilililo/fonts/Gilroy-Regular.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
        }}

        body {{
            font-family: 'Gilroy', sans-serif;
            padding: 20px;
            background-color: transparent;
            color: #fff;
            text-align: left;
            transform: scale(0.8);
            transform-origin: top center;
        }}

        h2 {{
            font-family: 'Orbitron', sans-serif;
            color: #afff00;
            text-align: center;
            text-shadow: 0 0 10px #afff00, 0 0 20px #afff00;
        }}

        pre {{
            background: #111;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 4px #afff00, 0 0 8px #afff00;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 16px;
            line-height: 1.5;
            color: #fff;
            font-family: 'Gilroy', sans-serif;
            text-shadow: none;
            overflow: hidden;
        }}

        a {{
            color: #afff00;
            text-decoration: underline;
        }}

        .long-neon {
    color: #39ff14;
    font-weight: 700;
    text-shadow:
        0 0 1px #39ff14,
        0 0 3px rgba(57, 255, 20, 0.45);
}

.short-neon {
    color: #ff3b3b;
    font-weight: 700;
    text-shadow:
        0 0 1px #ff3b3b,
        0 0 3px rgba(255, 59, 59, 0.45);
}
    </style>
</head>
<body>
    <h2>📢 {display_name}</h2>
    """

    msgs = messages_by_channel.get(channel_id, [])
    if msgs:
        linked_msg = linkify_coin_names(msgs[-1])
        html += f"<pre>{linked_msg}</pre>"
    else:
        html += "<pre>📭 아직 등록된 메시지가 없습니다.</pre>"

    html += "</body></html>"
    return html


# 🔹 메시지 30% 축소 버전
@app.route('/messages_small/<channel_id>')
def messages_small_html(channel_id):
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

    <!-- ✅ Orbitron + Gilroy 폰트 불러오기 -->
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
    <style>
        @font-face {{
            font-family: 'Gilroy';
            src: url('https://cdn.jsdelivr.net/gh/xilililo/fonts/Gilroy-Regular.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
        }}

        body {{
            font-family: 'Gilroy', sans-serif;
            padding: 20px;
            background-color: transparent;
            color: #fff;
            text-align: left;
            transform: scale(0.5);
            transform-origin: top center;
        }}

        h2 {{
            font-family: 'Orbitron', sans-serif;
            color: #afff00;
            text-align: center;
            text-shadow: 0 0 10px #afff00, 0 0 20px #afff00;
        }}

        pre {{
            background: #111;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 4px #afff00, 0 0 8px #afff00;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 16px;
            line-height: 1.5;
            color: #fff;
            font-family: 'Gilroy', sans-serif;
            text-shadow: none;
            overflow: hidden;
        }}

        a {{
            color: #afff00;
            text-decoration: underline;
        }}

        .long-neon {{
            color: #39ff14;
            font-weight: 700;
            text-shadow:
                0 0 4px #39ff14,
                0 0 8px #39ff14,
                0 0 16px #39ff14,
                0 0 24px #39ff14;
        }}

        .short-neon {{
            color: #ff3b3b;
            font-weight: 700;
            text-shadow:
                0 0 4px #ff3b3b,
                0 0 8px #ff3b3b,
                0 0 16px #ff3b3b,
                0 0 24px #ff3b3b;
        }}
    </style>
</head>
<body>
    <h2>📢 {display_name}</h2>
    """

    msgs = messages_by_channel.get(channel_id, [])
    if msgs:
        linked_msg = linkify_coin_names(msgs[-1])
        html += f"<pre>{linked_msg}</pre>"
    else:
        html += "<pre>📭 아직 등록된 메시지가 없습니다.</pre>"

    html += "</body></html>"
    return html


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
