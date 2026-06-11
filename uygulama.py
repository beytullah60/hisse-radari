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

# Session State ile hafıza oluşturma
if 'onceki_hisseler' not in st.session_state:
    st.session_state.onceki_hisseler = set()

# Filtreler
col1, col2, col3 = st.columns(3)
with col1: fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col2: hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])
with col3: dakika = st.number_input("Tarama (Dk):", min_value=5, max_value=60, value=5)
otomatik_tarama = st.toggle("🔄 Otomatik Tarama")

def tara():
    try:
        time.sleep(3)
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            df = df.sort_values(by='Rel Volume', ascending=False).head(5)
            
            # Güncel hisse listesini al
            yeni_hisse_listesi = set(df['Ticker'].tolist())
            
            # Mesaj oluşturma ve YENİ etiketi
            su_an = datetime.now(turkiye_saati).strftime("%H:%M")
            mesaj_satirlari = [f"--- {su_an} Raporu ---"]
            
            for _, row in df.iterrows():
                ticker = row['Ticker']
                yeni_mi = " (YENİ! ✨)" if ticker not in st.session_state.onceki_hisseler else ""
                mesaj_satirlari.append(f"{ticker}{yeni_mi} | Değişim: {row['Change']} | Hedef: ${float(str(row['Price']).replace('$',''))*1.03:.2f}")
            
            # Telegram'a gönder
            send_telegram_message("\n".join(mesaj_satirlari))
            
            # Hafızayı güncelle
            st.session_state.onceki_hisseler = yeni_hisse_listesi
            
            # Tabloya da yansıt
            df['Durum'] = df['Ticker'].apply(lambda x: "YENİ" if x not in st.session_state.onceki_hisseler else "Takip")
            st.dataframe(df[['Ticker', 'Price', 'Change', 'Durum']], use_container_width=True)
            
        else:
            st.warning("Hisse bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(dakika * 60)
        st.rerun()
