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

# --- HESAPLAMA (AL/SAT & HEDEF) ---
def tahmin_et(row):
    try:
        fiyat = float(str(row['Price']).replace('$', ''))
        degisim = float(str(row['Change']).replace('%', '').replace('+', ''))
        
        # Basit bir mantık: Değişim pozitifse AL, negatifse SAT
        sinyal = "AL 🟢" if degisim > 0 else "SAT 🔴"
        # Hedef: Fiyatın %3 üstü (Basit direnç tahmini)
        hedef = fiyat * 1.03
        return sinyal, f"${hedef:.2f}"
    except:
        return "N/A", "N/A"

# --- ARAYÜZ ---
col1, col2, col3 = st.columns(3)
with col1: fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col2: hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])
with col3: dakika = st.number_input("Otomatik Tarama (Dk):", min_value=1, value=2)

otomatik_tarama = st.toggle("🔄 Otomatik Taramayı Başlat")

def tara():
    try:
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            df = df.sort_values(by='Rel Volume', ascending=False).head(5)
            df['Change'] = df['Change'].apply(lambda x: f"{str(x).replace('%', '')}%")
            
            # Sinyal ve Hedef Ekle
            df[['Sinyal', 'Hedef']] = df.apply(lambda row: pd.Series(tahmin_et(row)), axis=1)
            
            df.insert(0, 'Sıra', range(1, len(df) + 1))
            
            # Tablo
            st.dataframe(
                df[['Sıra', 'Ticker', 'Price', 'Change', 'Sinyal', 'Hedef']],
                column_config={"Sinyal": st.column_config.TextColumn("İşlem Sinyali"), "Hedef": st.column_config.TextColumn("Hedef Tahmini")},
                use_container_width=True
            )
            
            # Telegram
            for _, row in df.iterrows():
                send_telegram_message(f"🏆 {row['Sıra']}. {row['Ticker']}\nSinyal: {row['Sinyal']} | Hedef: {row['Hedef']}")
        else:
            st.warning("Kriterlere uyan hisse yok.")
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(dakika * 60)
        st.rerun()
