import streamlit as st
import pandas as pd
import requests
import time
from finvizfinance.screener.overview import Overview

# --- TELEGRAM ---
def send_telegram_message(message):
    TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
    CHAT_ID = '8421496307'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except: pass

st.title("🚀 NASDAQ Top 10 Kazanç Radarı")

def tara():
    try:
        screener = Overview()
        # 3 Dolar altı tüm hisseleri çek
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': 'Under $3'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            # Yüzde değişim sütununu sayıya çevir (Örn: %12.5 -> 12.5)
            df['Change'] = df['Change'].str.replace('%', '').astype(float)
            
            # En çok yükselenden en aza ilk 10'u sırala
            df = df.sort_values(by='Change', ascending=False).head(10)
            
            # Ekranda göster
            st.dataframe(df[['Ticker', 'Price', 'Change', 'Volume']], use_container_width=True)
            
            # Telegram'a gönder
            rapor = "🔥 NASDAQ En Çok Yükselen 10 Hisse:\n\n"
            for _, row in df.iterrows():
                rapor += f"📈 {row['Ticker']} | Fiyat: {row['Price']} | Değişim: %{row['Change']}\n"
            
            send_telegram_message(rapor)
        else:
            st.warning("Hisse bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("📡 En Çok Kazandıranları Tara"):
    tara()
