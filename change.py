import pandas as pd
from yahoo_fin import stock_info as si
from datetime import datetime, timedelta

# ✅ 특정 기간의 USD/KRW 환율 가져오기 (Yahoo Finance)
def get_usd_to_krw_history(start_date, end_date):
    try:
        df = si.get_data('USDKRW=X', start_date=start_date, end_date=end_date)
        df = df[['close']]  # 종가 기준 환율
        df.index = df.index.date  # 날짜 포맷 정리
        df.rename(columns={'close': 'usd_to_krw'}, inplace=True)
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch historical exchange rates: {e}")

# ✅ 최근 100일치 환율 데이터 가져오기
def save_usd_to_krw_to_csv():
    # 시작일과 종료일 설정 (오늘 기준으로 100일 전까지)
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=100)
    
    # 환율 데이터 가져오기
    usd_to_krw_data = get_usd_to_krw_history(start_date, end_date)
    
    # 파일로 저장
    usd_to_krw_data.to_csv('usd_to_krw_100_days.csv', index=True)

    print("환율 데이터가 'usd_to_krw_100_days.csv' 파일에 저장되었습니다.")

# 함수 실행
save_usd_to_krw_to_csv()
