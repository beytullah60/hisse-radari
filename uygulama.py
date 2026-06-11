import streamlit as st
import pandas as pd
import requests
import time
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta, timezone

# --- TELEGRAM FONKSİYONU ---
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

# --- KULLANICI AYARLARI ---
col1, col2, col3 = st.columns(3)
with col1: fiyat = st.selectbox("Max Fiyat:", ["Under $1", "Under $2", "Under $5"])
with col2: hacim = st.selectbox("Min Hacim:", ["Over 1M", "Over 2M"])
with col3: dakika = st.number_input("Tarama Sıklığı (Dk):", min_value=5, max_value=60, value=5)

otomatik_tarama = st.toggle("🔄 Otomatik Taramayı Başlat")

# --- ANA TARAMA FONKSİYONU ---
def tara():
    try:
        # Finviz engellerini aşmak için kısa bir gecikme
        time.sleep(2)
        screener = Overview()
        
        # Filtreler: Sadece hacim patlaması olanlar
        filters = {'Exchange': 'NASDAQ', 'Price': fiyat, 'Current Volume': hacim, 'Relative Volume': 'Over 2'}
        screener.set_filter(filters_dict=filters)
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            # Sütun düzenleme
            df.columns = df.columns.str.strip()
            if 'Rel Volume' not in df.columns:
                cols = [c for c in df.columns if 'Rel' in c]
                if cols: df.rename(columns={cols[0]: 'Rel Volume'}, inplace=True)
            
            # Sıralama ve Numaralandırma
            df['Rel Volume'] = pd.to_numeric(df['Rel Volume'], errors='coerce')
            df = df.sort_values(by='Rel Volume', ascending=False).head(10)
            df.insert(0, 'Sıra', range(1, len(df) + 1))
            
            # Değişim formatı
            df['Change'] = df['Change'].apply(lambda x: f"{str(x).replace('%', '')}%")
            
            # Sinyal ve Hedef Tahmini
            df['Sinyal'] = df['Change'].apply(lambda x: "AL 🟢" if not str(x).startswith('-') else "SAT 🔴")
            df['Hedef'] = df['Price'].apply(lambda x: f"${float(str(x).replace('$',''))*1.03:.2f}")
            df['Grafik'] = df['Ticker'].apply(lambda x: f"https://www.tradingview.com/chart/?symbol=NASDAQ:{x}")
            
            # Tablo Gösterimi
            df_final = df[['Sıra', 'Ticker', 'Price', 'Change', 'Rel Volume', 'Sinyal', 'Hedef', 'Grafik']]
            st.dataframe(
                df_final.style.map(lambda x: 'color: green' if str(x).startswith('+') else ('color: red' if '-' in str(x) else ''), subset=['Change']),
                column_config={"Grafik": st.column_config.LinkColumn("Analiz", display_text="Grafiği Aç")},
                use_container_width=True
            )
            
            # Telegram
            su_an = datetime.now(turkiye_saati).strftime("%H:%M:%S")
            for _, row in df_final.iterrows():
                send_telegram_message(f"🏆 {row['Sıra']}. {row['Ticker']}\nFiyat: {row['Price']} | Değişim: {row['Change']}\nSinyal: {row['Sinyal']} | Hedef: {row['Hedef']}")
        else:
            st.warning("Şu an kriterlere uyan hisse yok.")
    except Exception as e:
        st.error(f"Sistem hatası (Finviz yoğun olabilir, lütfen bekleyin): {e}")

# --- ÇALIŞTIRMA ---
if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(dakika * 60)
        st.rerun()
