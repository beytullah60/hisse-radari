import streamlit as st
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timezone, timedelta

# --- TELEGRAM ---
def send_telegram_message(message):
    TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
    CHAT_ID = '8421496307'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        import requests
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except: pass

# --- AYARLAR ---
st.set_page_config(page_title="NASDAQ Pro Radar", layout="wide")
st.title("🚀 NASDAQ Profesyonel Patlama Radarı (YFinance)")

# Takip edilecek popüler NASDAQ hisseleri (Liste uzatılabilir)
hisse_listesi = ['ADTX', 'AERT', 'AKBA', 'BGM', 'CCHH', 'CCTG', 'COSM', 'DGNX', 'FLD', 'GLE', 'AAPL', 'NVDA', 'AMD']

otomatik_tarama = st.toggle("🔄 Otomatik Tarama")

def tara():
    try:
        data_list = []
        for ticker in hisse_listesi:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                fiyat = hist['Close'].iloc[-1]
                onceki_kapanis = stock.info.get('previousClose', fiyat)
                degisim = ((fiyat - onceki_kapanis) / onceki_kapanis) * 100
                
                data_list.append({
                    'Ticker': ticker,
                    'Price': round(fiyat, 3),
                    'Change': round(degisim, 2),
                    'Hedef': round(fiyat * 1.03, 3)
                })
        
        df = pd.DataFrame(data_list)
        df['Sinyal'] = df['Change'].apply(lambda x: "AL 🟢" if x > 0 else "SAT 🔴")
        
        st.dataframe(df, use_container_width=True)
        
        # Telegram
        for _, row in df.iterrows():
            send_telegram_message(f"🏆 {row['Ticker']} | Fiyat: ${row['Price']} | Hedef: ${row['Hedef']} | Sinyal: {row['Sinyal']}")
            
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(300) # 5 dakika
        st.rerun()
