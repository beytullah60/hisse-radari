import os
import streamlit as st
import pandas as pd
import time
from finvizfinance.screener.overview import Overview

# Token çekme stratejisi: Önce Streamlit secrets, olmazsa sistem değişkeni
def get_token():
    try:
        return st.secrets["TELEGRAM_TOKEN"]
    except:
        return os.environ.get("TELEGRAM_TOKEN")

TOKEN = get_token()
CHAT_ID = '8421496307'

# --- TELEGRAM ---
def send_telegram_message(message):
    if not TOKEN: 
        st.error("Telegram Token bulunamadı!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        import requests
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        st.error(f"Mesaj gönderilemedi: {e}")

# --- AYARLAR ---
st.set_page_config(page_title="NASDAQ 3$ Altı Radarı", layout="wide")
st.title("🚀 NASDAQ Profesyonel 3$ Altı Hisse Radarı")

otomatik_tarama = st.toggle("🔄 Otomatik Tarama (5 Dakikada Bir)")

def tara():
    try:
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': 'Under $3'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            df['Change'] = df['Change'].astype(str).str.replace('%', '')
            df['Change'] = pd.to_numeric(df['Change'], errors='coerce').fillna(0)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
            
            st.write("### NASDAQ 3$ Altı Tüm Hisseler")
            st.dataframe(df, use_container_width=True)
            
            top_10 = df.sort_values(by='Change', ascending=False).head(10)
            rapor = "🔥 NASDAQ En Çok Yükselen 10 Hisse:\n\n"
            for _, row in top_10.iterrows():
                rapor += f"📈 {row['Ticker']} | Fiyat: ${row['Price']} | Değişim: %{row['Change']}\n"
            
            # Telegram'a mesajı gönder
            send_telegram_message(rapor)
            st.success("Telegram'a güncel rapor gönderildi!")
        else:
            st.warning("Hisse bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")

# Buton veya Otomatik mod tetikleyici
if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(300) # 5 dakika bekle
        st.rerun() # Sayfayı yenile ve döngüye devam et
