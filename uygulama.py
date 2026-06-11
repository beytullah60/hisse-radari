import streamlit as st
import pandas as pd
import requests
import time
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta, timezone

# --- TELEGRAM ---
def send_telegram_message(message):
    TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
    CHAT_ID = '8421496307'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except:
        pass

# --- AYARLAR ---
turkiye_saati = timezone(timedelta(hours=3))
st.set_page_config(page_title="NASDAQ Pro Radar", layout="wide")
st.title("🚀 NASDAQ Profesyonel Patlama Radarı")

# Filtreler
col1, col2, col3 = st.columns(3)
with col1:
    fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col2:
    hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])
with col3:
    otomatik_tarama = st.toggle("🔄 Otomatik Tarama (Aktif Et)")

# Tarama Fonksiyonu
def tara():
    try:
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            gosterilecek_sutunlar = ['Ticker', 'Company', 'Price', 'Change', 'Volume']
            df_final = df[gosterilecek_sutunlar].copy()
            df_final['Grafik'] = df_final['Ticker'].apply(lambda x: f"https://www.tradingview.com/chart/?symbol=NASDAQ:{x}")
            
            # Renklendirme
            st.dataframe(
                df_final.style.map(lambda x: 'color: green' if str(x).startswith('+') else ('color: red' if str(x).startswith('-') else ''), subset=['Change']),
                column_config={"Grafik": st.column_config.LinkColumn("Analiz", display_text="Grafiği Aç")},
                use_container_width=True
            )
            
            # Telegram Bildirimi
            su_an = datetime.now(turkiye_saati).strftime("%H:%M:%S")
            for _, row in df_final.head(5).iterrows():
                send_telegram_message(f"🚨 Sinyal [{su_an}]: {row['Ticker']} | Fiyat: {row['Price']} | Değişim: {row['Change']}")
        else:
            st.warning("Şu an kriterlere uygun hisse bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")

# Buton veya Otomatik Tarama
if st.button("📡 Piyasayı Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        st.info("⏳ Otomatik mod aktif. 2 dakika sonra sayfa yenilenecek...")
        time.sleep(120)
        st.rerun()
