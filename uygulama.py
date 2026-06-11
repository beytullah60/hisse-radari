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
        time.sleep(2)
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            
            # GÜVENLİK: Sütun ismini düzelt ve eksikse 0 ata
            if 'Rel Volume' not in df.columns:
                cols = [c for c in df.columns if 'Rel' in c]
                if cols: df.rename(columns={cols[0]: 'Rel Volume'}, inplace=True)
                else: df['Rel Volume'] = 0
            
            # Sayısal çevrim hatasını önle
            df['Rel Volume'] = pd.to_numeric(df['Rel Volume'], errors='coerce').fillna(0)
            df = df.sort_values(by='Rel Volume', ascending=False).head(10)
            
            # Gösterim işlemleri
            df['Change'] = df['Change'].apply(lambda x: f"{str(x).replace('%', '')}%")
            df['Sinyal'] = df['Change'].apply(lambda x: "AL 🟢" if not str(x).startswith('-') else "SAT 🔴")
            df['Grafik'] = df['Ticker'].apply(lambda x: f"https://www.tradingview.com/chart/?symbol=NASDAQ:{x}")
            
            st.dataframe(
                df[['Ticker', 'Price', 'Change', 'Rel Volume', 'Sinyal', 'Grafik']].style.map(
                    lambda x: 'color: green' if str(x).startswith('+') else ('color: red' if '-' in str(x) else ''), 
                    subset=['Change']
                ),
                column_config={"Grafik": st.column_config.LinkColumn("Analiz", display_text="Grafiği Aç")},
                use_container_width=True
            )
            
            # Telegram
            for _, row in df.iterrows():
                send_telegram_message(f"🏆 {row['Ticker']} | Fiyat: {row['Price']} | RVol: {row['Rel Volume']} | {row['Sinyal']}")
        else:
            st.warning("Şu an kriterlere uyan hisse yok.")
    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(dakika * 60)
        st.rerun()
