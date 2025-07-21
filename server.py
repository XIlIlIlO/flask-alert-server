from flask import Flask, request
import os
from binance.client import Client
from flask import jsonify  # 이미 있을 수도 있음

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
api_key = os.getenv("XH7JN637MfMSELLQjpviyLHuaiNvICWYTi2fssTVJQDDQu0lcdczaK64WFqI2xjQ")
api_secret = os.getenv("CCDDXGfxD1PJCSubXTc406DbFP5pBTuDbZ9WzrrC4nicCpVLtcuQyIrjkl4IKQpr")
client = Client(api_key, api_secret)

def get_usdt_symbols():
    exchange_info = client.futures_exchange_info()
    return [s['symbol'] for s in exchange_info['symbols']
            if s['quoteAsset'] == 'USDT'
            and s['contractType'] == 'PERPETUAL'
            and not s['symbol'].startswith('LD')]

def get_15m_volatility(symbol):
    try:
        klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=15)
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        open_price = float(klines[0][1])
        close_price = float(klines[-1][4])
        high = max(highs)
        low = min(lows)
        volatility = abs((high - low) / low) * 100
        color = "green" if close_price > open_price else "red"
        return {"symbol": symbol, "volatility": volatility, "color": color}
    except:
        return None

@app.route("/top_volatility")
def top_volatility():
    symbols = get_usdt_symbols()
    data = []
    for sym in symbols:
        result = get_15m_volatility(sym)
        if result:
            data.append(result)
    sorted_data = sorted(data, key=lambda x: x['volatility'], reverse=True)[:30]
    return jsonify(sorted_data)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
