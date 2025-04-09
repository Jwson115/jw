import ccxt
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from yahoo_fin import stock_info as si
from forex_python.converter import CurrencyRates

# ✅ 환율 데이터 가져오기 (forex-python 사용)
def get_usd_to_krw_history(start_date, end_date):
    c = CurrencyRates()
    dates = pd.date_range(start_date, end_date)
    rates = [c.get_rate('USD', 'KRW', date) for date in dates]
    df = pd.DataFrame({'timestamp': dates, 'usd_to_krw': rates})
    df.set_index('timestamp', inplace=True)
    return df

# ✅ Binance에서 XRP 가격 가져오기 (재시도 로직 추가)
def get_xrp_binance(retries=3, delay=2):
    for i in range(retries):
        try:
            exchange = ccxt.binance()
            symbol = 'XRP/USDT'
            timeframe = '1d'
            limit = 100
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date

            # 환율 데이터 가져오기
            start_date = df['timestamp'].min() - timedelta(days=1)
            end_date = df['timestamp'].max() + timedelta(days=1)
            exchange_rates = get_usd_to_krw_history(start_date, end_date)

            # 날짜별 환율 적용
            df = df.merge(exchange_rates, left_on='timestamp', right_index=True, how='left')
            df['close'] = df['close'] * df['usd_to_krw']  # USDT → KRW 변환

            return df[['timestamp', 'close']]
        except Exception as e:
            if i == retries - 1:
                raise Exception(f"Failed to fetch Binance data after {retries} retries: {e}")
            time.sleep(delay)

# ✅ Upbit에서 XRP 가격 가져오기 (재시도 로직 추가)
def get_xrp_upbit(retries=3, delay=2):
    for i in range(retries):
        try:
            url = "https://api.upbit.com/v1/candles/days"
            params = {"market": "KRW-XRP", "count": 100}
            response = requests.get(url, params=params)
            data = response.json()
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['candle_date_time_kst']).dt.date
            df.rename(columns={'trade_price': 'close'}, inplace=True)
            return df[['timestamp', 'close']]
        except Exception as e:
            if i == retries - 1:
                raise Exception(f"Failed to fetch Upbit data after {retries} retries: {e}")
            time.sleep(delay)

# ✅ 김프(Korea Premium) 계산
def calculate_korea_premium():
    binance_data = get_xrp_binance()
    upbit_data = get_xrp_upbit()

    # ✅ 두 데이터 병합 (timestamp 기준)
    merged_data = pd.merge(binance_data, upbit_data, on='timestamp', how='inner', suffixes=('_binance', '_upbit'))

    # ✅ 김프 계산
    merged_data['premium'] = ((merged_data['close_upbit'] - merged_data['close_binance']) / merged_data['close_binance']) * 100

    return merged_data[['timestamp', 'close_binance', 'close_upbit', 'premium']]

# ✅ 차트 그리기
def plot_xrp_charts():
    binance_data = calculate_korea_premium()
    upbit_data = get_xrp_upbit()

    # 환율 데이터 가져오기
    usd_to_krw_data = get_usd_to_krw_history(binance_data['timestamp'].min(), binance_data['timestamp'].max())

    # Binance 데이터와 환율 데이터 병합 (날짜 기준)
    merged_data = pd.merge(binance_data, usd_to_krw_data, left_on='timestamp', right_index=True, how='outer')

    # Upbit 데이터 병합
    merged_data = pd.merge(merged_data, upbit_data, on='timestamp', how='outer')

    # NaN 값 보간 (선형 보간)
    merged_data['close_binance'] = merged_data['close_binance'].interpolate()
    merged_data['premium'] = merged_data['premium'].interpolate()
    merged_data['usd_to_krw'] = merged_data['usd_to_krw'].interpolate()
    merged_data['close_upbit'] = merged_data['close_upbit'].interpolate()

    # 날짜 정렬
    merged_data.sort_values('timestamp', inplace=True)

    # 차트 그리기
    fig, axes = plt.subplots(4, 1, figsize=(12, 16), sharex=True)

    # Binance XRP 가격 차트
    axes[0].plot(merged_data['timestamp'], merged_data['close_binance'], label='Binance XRP/KRW', color='blue', marker='o', linestyle='-')
    axes[0].set_ylabel("Price (KRW)")
    axes[0].set_title("Binance XRP/KRW Price Chart")
    axes[0].legend()
    axes[0].grid()

    # Upbit XRP 가격 차트
    axes[1].plot(merged_data['timestamp'], merged_data['close_upbit'], label='Upbit XRP/KRW', color='red', marker='o', linestyle='-')
    axes[1].set_ylabel("Price (KRW)")
    axes[1].set_title("Upbit XRP/KRW Price Chart")
    axes[1].legend()
    axes[1].grid()

    # 김프 차트
    axes[2].plot(merged_data['timestamp'], merged_data['premium'], label='Korea Premium (%)', color='green', marker='o', linestyle='-')
    axes[2].axhline(0, color='gray', linestyle='--', linewidth=1)
    axes[2].set_ylabel("Premium (%)")
    axes[2].set_title("XRP Korea Premium")
    axes[2].legend()
    axes[2].grid()

    # 환율 차트 (USD/KRW)
    axes[3].plot(merged_data['timestamp'], merged_data['usd_to_krw'], label='USD/KRW Exchange Rate', color='purple', marker='o', linestyle='-')
    axes[3].set_ylabel("Exchange Rate (KRW)")
    axes[3].set_title("USD/KRW Exchange Rate")
    axes[3].legend()
    axes[3].grid()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ✅ 실행
plot_xrp_charts()