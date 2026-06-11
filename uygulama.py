import streamlit as st
import pandas as pd
import time
from finvizfinance.screener.overview import Overview

# --- TELEGRAM ---
def send_telegram_message(message):
    TOKEN = '8701740133:AAEL0-5Z_zyMFGMfvgwsGVyNNj8KnGqheuk'
    CHAT_ID = '8421496307'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        import requests
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except: pass

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="NASDAQ 3$ Altı Radarı", layout="wide")
st.title("🚀 NASDAQ Profesyonel 3$ Altı Hisse Radarı")

otomatik_tarama = st.toggle("🔄 Otomatik Tarama (5 Dakikada Bir)")

def tara():
    try:
        # Finviz üzerinden 3 dolar altı tüm NASDAQ hisselerini çek
        screener = Overview()
        screener.set_filter(filters_dict={'Exchange': 'NASDAQ', 'Price': 'Under $3'})
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            # Sütunları düzenle ve sayısal formata çevir
            df['Change'] = df['Change'].str.replace('%', '').astype(float)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            
            # 1. EKRAN İÇİN: Tüm listeyi göster
            st.write("### NASDAQ 3$ Altı Tüm Hisseler")
            st.dataframe(df, use_container_width=True)
            
            # 2. TELEGRAM İÇİN: En yüksek yükselişi olan ilk 10'u seç
            top_10 = df.sort_values(by='Change', ascending=False).head(10)
            
            rapor = "🔥 NASDAQ En Çok Yükselen 10 Hisse:\n\n"
            for _, row in top_10.iterrows():
                rapor += f"📈 {row['Ticker']} | Fiyat: ${row['Price']} | Değişim: %{row['Change']}\n"
            
            send_telegram_message(rapor)
            st.success("Telegram'a güncel rapor gönderildi!")
        else:
            st.warning("Hisse bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")

if st.button("📡 Şimdi Tara") or otomatik_tarama:
    tara()
    if otomatik_tarama:
        time.sleep(300) # 5 dakika
        st.rerun()
