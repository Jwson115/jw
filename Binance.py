import ccxt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import requests

# ExchangeRate-API를 통해 USD/KRW 환율 가져오기
def get_usd_to_krw():
    api_key = "YOUR_EXCHANGERATE_API_KEY"  # 발급받은 API 키 입력
    url = f"https://v6.exchangerate-api.com/v6/2f0e5a8687e6b79ff46aa3db/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates']['KRW']  # USD/KRW 환율 반환
    else:
        raise Exception("Failed to fetch exchange rate")

# 바이낸스 API 연결
exchange = ccxt.binance()

# 리플(XRP)의 USDT 거래쌍 심볼
symbol = 'XRP/USDT'

# 일봉(1d) 간격으로 최근 100개의 캔들 데이터 가져오기
timeframe = '1d'
limit = 100
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

# 데이터를 DataFrame으로 변환
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # 타임스탬프를 날짜 형식으로 변환

# USD/KRW 환율 가져오기
usd_to_krw = get_usd_to_krw()

# KRW로 가격 변환
df['open_krw'] = df['open'] * usd_to_krw
df['high_krw'] = df['high'] * usd_to_krw
df['low_krw'] = df['low'] * usd_to_krw
df['close_krw'] = df['close'] * usd_to_krw

# 캔들차트 그리기
fig, ax = plt.subplots(figsize=(12, 6))

# 캔들스틱 데이터 설정
for i in range(len(df)):
    color = 'green' if df['close_krw'][i] > df['open_krw'][i] else 'red'  # 상승(초록), 하락(빨강)
    ax.plot([df['timestamp'][i], df['timestamp'][i]], [df['low_krw'][i], df['high_krw'][i]], color=color, linewidth=1)
    ax.add_patch(plt.Rectangle((df['timestamp'][i] - pd.Timedelta(hours=12), df['open_krw'][i]), 
                               pd.Timedelta(hours=24), 
                               df['close_krw'][i] - df['open_krw'][i], 
                               facecolor=color, edgecolor='black'))

# 그래프 설정
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.set_xlabel('Time')
ax.set_ylabel('Price (KRW)')
ax.set_title(f'{symbol} {timeframe} Candlestick Chart (KRW)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# 그래프 출력
plt.show()