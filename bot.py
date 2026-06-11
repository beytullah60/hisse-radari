import time
import requests
import pandas as pd
from finvizfinance.screener.overview import Overview

TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
CHAT_ID = '8421496307'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except: pass

def run_bot():
    while True:
        try:
            screener = Overview()
            screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': 'Under $3'})
            df = screener.screener_view()
            
            if df is not None and not df.empty:
                df['Change'] = df['Change'].astype(str).str.replace('%', '')
                df['Change'] = pd.to_numeric(df['Change'], errors='coerce').fillna(0)
                top_10 = df.sort_values(by='Change', ascending=False).head(10)
                
                rapor = "🔥 NASDAQ En Çok Yükselen 10 Hisse (Otomatik):\n\n"
                for _, row in top_10.iterrows():
                    rapor += f"📈 {row['Ticker']} | Fiyat: ${row['Price']} | Değişim: %{row['Change']}\n"
                send_telegram_message(rapor)
        except Exception as e:
            print(f"Hata: {e}")
        
        time.sleep(300) # 5 dakika bekle

if __name__ == "__main__":
    run_bot()
