import ccxt
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime
import os
import time

# ✅ USD → KRW 환율 가져오기
def get_usd_to_krw():
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")  # 환경 변수에서 API 키 가져오기
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['conversion_rates']['KRW']
    except Exception as e:
        raise Exception(f"Failed to fetch exchange rate: {e}")

# ✅ Binance에서 XRP 가격 가져오기 (USDT 기준)
def get_xrp_binance():
    exchange = ccxt.binance()
    symbol = 'XRP/USDT'
    timeframe = '1d'
    limit = 100
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'] + pd.Timedelta(hours=9)  # UTC → KST 변환
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch Binance data: {e}")

# ✅ Upbit에서 XRP 가격 가져오기 (KRW 기준)
def get_xrp_upbit(retries=3, delay=2):
    for i in range(retries):
        try:
            url = "https://api.upbit.com/v1/candles/days"
            params = {"market": "KRW-XRP", "count": 100}
            response = requests.get(url, params=params)
            data = response.json()
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['candle_date_time_kst'])
            df.rename(columns={'trade_price': 'close'}, inplace=True)  # 'trade_price' → 'close' 변경
            return df[['timestamp', 'open', 'high', 'low', 'close', 'candle_acc_trade_volume']]
        except Exception as e:
            if i == retries - 1:
                raise Exception(f"Failed to fetch Upbit data after {retries} retries: {e}")
            time.sleep(delay)

# ✅ 김프(Korea Premium) 계산
def calculate_korea_premium():
    usd_to_krw = get_usd_to_krw()
    binance_data = get_xrp_binance()[['timestamp', 'close']]
    upbit_data = get_xrp_upbit()[['timestamp', 'close']]

    # ✅ timestamp를 날짜 단위로 변환
    binance_data['timestamp'] = binance_data['timestamp'].dt.date
    upbit_data['timestamp'] = upbit_data['timestamp'].dt.date

    # ✅ 두 데이터 병합 (timestamp 기준)
    merged_data = pd.merge(binance_data, upbit_data, on='timestamp', how='inner', suffixes=('_binance', '_upbit'))

    # ✅ Binance 가격을 원화로 변환 후 김프 계산
    merged_data['binance_price_krw'] = merged_data['close_binance'] * usd_to_krw
    merged_data['premium'] = ((merged_data['close_upbit'] - merged_data['binance_price_krw']) / merged_data['binance_price_krw']) * 100

    return merged_data[['timestamp', 'premium']]

# ✅ Binance XRP 캔들차트 그리기
def plot_binance_xrp_candles():
    binance_data = get_xrp_binance()

    plt.figure(figsize=(12, 6))
    plt.plot(binance_data['timestamp'], binance_data['close'], label='Binance XRP/USDT', color='blue', marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Price (USDT)")
    plt.title("Binance XRP/USDT Price Chart")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.show()

# ✅ Upbit XRP 캔들차트 그리기
def plot_upbit_xrp_candles():
    upbit_data = get_xrp_upbit()

    plt.figure(figsize=(12, 6))
    plt.plot(upbit_data['timestamp'], upbit_data['close'], label='Upbit XRP/KRW', color='red', marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Price (KRW)")
    plt.title("Upbit XRP/KRW Price Chart")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.show()

# ✅ 김프 그래프 그리기
def plot_korea_premium():
    premium_data = calculate_korea_premium()
    
    plt.figure(figsize=(12, 6))
    plt.plot(premium_data['timestamp'], premium_data['premium'], marker='o', linestyle='-', color='green', label='Korea Premium (%)')
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.xlabel("Date")
    plt.ylabel("Premium (%)")
    plt.title("XRP Korea Premium")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.show()

# ✅ 실행 (세 개의 그래프를 출력)
def plot_xrp_charts():
    plot_binance_xrp_candles()
    plot_upbit_xrp_candles()
    plot_korea_premium()

# ✅ 메인 실행
plot_xrp_charts()
