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
    except: pass

# --- AYARLAR ---
turkiye_saati = timezone(timedelta(hours=3))
st.set_page_config(page_title="NASDAQ Pro Radar", layout="wide")
st.title("🚀 NASDAQ Profesyonel Patlama Radarı")

# --- ARAYÜZ ---
col1, col2, col3 = st.columns(3)
with col1: fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col2: hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])
with col3: dakika = st.number_input("Otomatik Tarama (Dk):", min_value=1, value=2)
otomatik_tarama = st.toggle("🔄 Otomatik Taramayı Başlat")

def tara():
    try:
        screener = Overview()
        # Filtreleri uyguluyoruz
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            # SÜTUN İSİMLERİNİ GÜVENLİ HALE GETİRME
            df.columns = df.columns.str.strip() # Boşlukları temizle
            
            # Eğer Rel Volume farklı bir isimle gelirse diye manuel atama
            if 'Rel Volume' not in df.columns:
                # Sütunları tara, içinde 'Rel' geçen var mı bak
                cols = [c for c in df.columns if 'Rel' in c]
                if cols: df.rename(columns={cols[0]: 'Rel Volume'}, inplace=True)
            
            # Artık Rel Volume kesin var, işlemlere devam edebiliriz
            df = df.sort_values(by='Rel Volume', ascending=False).head(10)
            df['Change'] = df['Change'].apply(lambda x: f"{str(x).replace('%', '')}%")
            
            # Tahmin
            df['Sinyal'] = df['Change'].apply(lambda x: "AL 🟢" if not str(x).startswith('-') else "SAT 🔴")
            df['Hedef'] = df['Price'].apply(lambda x: f"${float(str(x).replace('$',''))*1.03:.2f}")
            
            # GÖSTERİM
            df_final = df[['Ticker', 'Price', 'Change', 'Rel Volume', 'Sinyal', 'Hedef']]
            
            st.dataframe(
                df_final.style.map(lambda x: 'color: green' if str(x).startswith('+') else ('color: red' if '-' in str(x) else ''), subset=['Change']),
                use_container_width=True
            )
            
            # Telegram
            for _, row in df_final.iterrows():
                send_telegram_message(f"🏆 {row['Ticker']} | Fiyat: {row['Price']} | RVol: {row['Rel Volume']} | Sinyal: {row['Sinyal']}")
        else:
            st.warning("Kriterlere uyan hisse yok.")
    except Exception as e:
        st.error(f"Sistem hatası: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(dakika * 60)
        st.rerun()
