import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def get_xrp_daily_candles():
    # 업비트 API URL (일봉 데이터 요청)
    url = "https://api.upbit.com/v1/candles/days"
    
    # 파라미터 설정 (리플(XRP)의 마켓 코드는 KRW-XRP, 최대 200개의 데이터 요청)
    params = {
        "market": "KRW-XRP",
        "count": 200  # 최근 200일 데이터
    }
    
    # API 요청
    response = requests.get(url, params=params)
    
    # 응답 확인
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def plot_daily_candles(candles):
    # 데이터 파싱
    dates = [datetime.strptime(candle['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for candle in candles]
    opening_prices = [candle['opening_price'] for candle in candles]
    closing_prices = [candle['trade_price'] for candle in candles]
    high_prices = [candle['high_price'] for candle in candles]
    low_prices = [candle['low_price'] for candle in candles]

    # 차트 그리기
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title("XRP Daily Candlestick Chart (Upbit)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (KRW)")

    # 캔들스틱 그리기 (barplot으로 색상 적용)
    for i in range(len(dates)):
        # 양봉 (상승) - 초록색
        if opening_prices[i] < closing_prices[i]:
            ax.bar(dates[i], closing_prices[i] - opening_prices[i], bottom=opening_prices[i], width=0.8, color='#66FF66', alpha=0.7)
        # 음봉 (하락) - 빨간색
        elif opening_prices[i] > closing_prices[i]:
            ax.bar(dates[i], opening_prices[i] - closing_prices[i], bottom=closing_prices[i], width=0.8, color='#FF6347', alpha=0.7)
        # 보합 (시가와 종가가 같을 때) - 금색
        else:
            ax.bar(dates[i], closing_prices[i] - opening_prices[i], bottom=opening_prices[i], width=0.8, color='#FFD700', alpha=0.7)

        # 캔들의 위아래 "꼬리"를 그리기 위해
        ax.plot([dates[i], dates[i]], [low_prices[i], high_prices[i]], color='black', linewidth=1)

    # 날짜 형식 설정
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate()  # 날짜 레이블 회전

    ax.grid(True)
    plt.show()

# 일봉 데이터 가져오기
candles = get_xrp_daily_candles()

if candles:
    # 차트 그리기
    plot_daily_candles(candles)
