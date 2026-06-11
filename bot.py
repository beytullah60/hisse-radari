import os
import yfinance as yf
import pandas as pd
import requests
from finvizfinance.screener.overview import Overview

# Token'ı GitHub Secrets'tan alıyoruz
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = '8421496307'

def send_telegram_message(message):
    if not TOKEN: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except: pass

def tara():
    try:
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': 'Under $3'})
        df = screener.screener_view()
        
        if df is None or df.empty: return

        tickers = df['Ticker'].head(15).tolist()
        data_list = []
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('preMarketPrice') or info.get('regularMarketPrice') or info.get('currentPrice')
            prev_close = info.get('previousClose')
            
            if price and prev_close:
                change = ((price - prev_close) / prev_close) * 100
                data_list.append({'Ticker': ticker, 'Price': round(price, 3), 'Change': round(change, 2)})
        
        res = pd.DataFrame(data_list).sort_values(by='Change', ascending=False).head(10)
        rapor = "🔥 NASDAQ Fırsat Radarı:\n\n"
        for _, row in res.iterrows():
            rapor += f"📈 {row['Ticker']} | Fiyat: ${row['Price']} | Değişim: %{row['Change']}\n"
        
        send_telegram_message(rapor)
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    tara()
