import streamlit as st
import pandas as pd
import requests
import time
from finvizfinance.screener.overview import Overview
from datetime import datetime, timezone, timedelta

# --- TELEGRAM AYARLARI ---
TELEGRAM_BOT_TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
TELEGRAM_CHAT_ID = '8421496307'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except:
        pass
# -------------------------

# --- FORMATLAYICILAR ---
def hacim_formatla(vol):
    try:
        v = float(str(vol).replace(',', ''))
        if v >= 1000000: return f"{v/1000000:.2f} Milyon"
        elif v >= 1000: return f"{v/1000:.1f} Bin"
        return str(int(v))
    except: return str(vol)

def yuzde_formatla(oran):
    try:
        return float(str(oran).replace('%', '').replace(',', ''))
    except: return 0.0

# --- RENKLENDİRME FONKSİYONU ---
def renklendir(val):
    if isinstance(val, str) and '+' in val:
        return 'color: green'
    elif isinstance(val, str) and '-' in val:
        return 'color: red'
    return ''

# --- ARAYÜZ ---
st.set_page_config(page_title="NASDAQ Canlı Radar", layout="wide")
st.title("🎯 NASDAQ Ani Patlama Radarı")

# Filtreler (Kodun geri kalanı aynı)
fiyat_secimi = st.selectbox("Maksimum Fiyat:", ["Under $1", "Under $2", "Under $5"], index=0)
hacim_secimi = st.selectbox("Min. Hacim:", ["Over 1M", "Over 2M", "Over 5M"], index=0)
otomatik_tarama = st.toggle("🔄 Otomatik Tarama")

tz_TR = timezone(timedelta(hours=3))

if st.button("📡 Piyasayı Tara") or otomatik_tarama:
    try:
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': fiyat_secimi, 'Current Volume': hacim_secimi, 'Relative Volume': 'Over 2'})
        df = screener.screener_view()
        
        if not df.empty:
            df_goster = df[['Ticker', 'Company', 'Price', 'Change', 'Volume']].copy()
            df_goster['Volume'] = df_goster['Volume'].apply(hacim_formatla)
            
            # Değişim oranını formatla ve renklendirme için hazırla
            df_goster['Change_Raw'] = df['Change'].apply(yuzde_formatla)
            df_goster['Günlük Değişim (%)'] = df_goster['Change_Raw'].apply(lambda x: f"+%{x:.2f}" if x > 0 else f"-%{abs(x):.2f}")
            
            df_final = df_goster[['Ticker', 'Company', 'Price', 'Günlük Değişim (%)', 'Volume']]
            df_final.columns = ['Hisse', 'Şirket', 'Fiyat', 'Değişim', 'Hacim']
            
            # TABLOYU RENKLENDİR
            st.dataframe(df_final.style.applymap(lambda x: 'color: green' if str(x).startswith('+') else ('color: red' if str(x).startswith('-') else ''), subset=['Değişim']), use_container_width=True)
            
            # Telegram'a bildirim (Aynı kalıyor)
            # ... (Buraya eski Telegram kodunu ekleyebilirsiniz)
            
        else:
            st.info("Hisse bulunamadı.")
    except Exception as e:
        st.error("Bir hata oluştu.")
