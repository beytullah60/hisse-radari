import streamlit as st
import pandas as pd
import requests
import time
from finvizfinance.screener.overview import Overview
from datetime import datetime, timezone, timedelta

# --- TELEGRAM ---
def send_telegram_message(message):
    TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
    CHAT_ID = '8421496307'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except: pass

# --- AYARLAR ---
turkiye_saati = timezone(timedelta(hours=3))
st.set_page_config(page_title="NASDAQ Pro Radar", layout="wide")
st.title("🚀 NASDAQ Profesyonel Patlama Radarı")

# Filtreler
col1, col2, col3 = st.columns(3)
with col1: fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col2: hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])
with col3: dakika = st.number_input("Tarama (Dk):", min_value=5, max_value=60, value=5)

otomatik_tarama = st.toggle("🔄 Otomatik Tarama")

def tara():
    try:
        time.sleep(3)
        from finvizfinance.util import web_scraping
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2'})
        df = screener.screener_view(verbose=0)
        
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            
            # Veri düzenleme
            df = df.sort_values(by='Price', ascending=False).head(5)
            df['Change'] = df['Change'].apply(lambda x: f"{str(x).replace('%', '')}%")
            df['Sinyal'] = df['Change'].apply(lambda x: "AL 🟢" if not str(x).startswith('-') else "SAT 🔴")
            df['Hedef'] = (df['Price'] * 1.03).round(2)
            
            # Tablo göster
            st.dataframe(df[['Ticker', 'Price', 'Change', 'Sinyal', 'Hedef']], use_container_width=True)
            
            # TELEGRAM: Her seferinde tekrar gönder
            su_an = datetime.now(turkiye_saati).strftime("%H:%M")
            mesaj_baslik = f"--- {su_an} Canlı Raporu ---\n"
            
            for _, row in df.iterrows():
                mesaj = f"🏆 {row['Ticker']} | Fiyat: ${row['Price']} | Hedef: ${row['Hedef']} | Sinyal: {row['Sinyal']}"
                send_telegram_message(mesaj)
                
        else:
            st.warning("Hisse bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(dakika * 60)
        st.rerun()
