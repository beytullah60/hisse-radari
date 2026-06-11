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
    except:
        pass

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="NASDAQ Pro Radar", layout="wide")
st.title("🚀 NASDAQ Profesyonel Patlama Radarı")

# Filtreler
col1, col2, col3 = st.columns(3)
with col1:
    sektor = st.selectbox("Sektör:", ["Any", "Technology", "Healthcare", "Financial", "Energy"])
with col2:
    fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col3:
    hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])

if st.button("📡 Piyasayı Profesyonel Tara"):
    try:
        screener = Overview()
        filters = {'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2', 'Performance': 'Today Up'}
        if sektor != "Any": filters['Sector'] = sektor
        
        screener.set_filter(filters_dict=filters)
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            df = df[['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Rel Volume']]
            df.columns = ['Hisse', 'Şirket', 'Sektör', 'Fiyat', 'Değişim', 'Hacim', 'RVol']
            
            # TradingView Linki
            df['Grafik'] = df['Hisse'].apply(lambda x: f"https://www.tradingview.com/chart/?symbol=NASDAQ:{x}")
            
            # Renklendirme ve Gösterim
            st.dataframe(
                df.style.map(lambda x: 'color: green' if str(x).startswith('+') else ('color: red' if str(x).startswith('-') else ''), subset=['Değişim']),
                column_config={"Grafik": st.column_config.LinkColumn("Analiz", display_text="Grafiği Aç")},
                use_container_width=True
            )
            
            # Telegram'a bildirim (İlk 5 hisse)
            for _, row in df.head(5).iterrows():
                send_telegram_message(f"🚨 Sinyal: {row['Hisse']} | Fiyat: {row['Fiyat']} | RVol: {row['RVol']}")
        else:
            st.warning("Kriterlere uygun hisse bulunamadı.")
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
