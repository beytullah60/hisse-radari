import streamlit as st
import pandas as pd
import requests
import time
from finvizfinance.screener.overview import Overview
from datetime import datetime

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

st.set_page_config(page_title="NASDAQ Canlı Radar", layout="wide")

st.title("🎯 NASDAQ Ani Patlama Radarı")
st.markdown("**Amacımız:** Ucuz olan, aniden devasa hacim giren ve yükseliş trendini başlatan hisseleri anında tespit etmek.")

# Kullanıcı Filtreleri
col1, col2 = st.columns(2)
with col1:
    fiyat_secimi = st.selectbox("Maksimum Fiyat Hedefi:", ["Under $1", "Under $2", "Under $3", "Under $5"], index=0)
with col2:
    hacim_secimi = st.selectbox("Minimum Günlük Hacim:", ["Over 1M", "Over 2M", "Over 5M"], index=0)

st.write("---")

# --- OTOMATİK TARAMA AYARLARI ---
col3, col4 = st.columns(2)
with col3:
    otomatik_tarama = st.toggle("🔄 Otomatik Taramayı Aç (Sayfa açık kaldıkça çalışır)")
with col4:
    bekleme_suresi = st.number_input("Kaç dakikada bir tarasın?", min_value=1, max_value=60, value=2)

st.write("---")

# Butona basılırsa VEYA Otomatik Tarama açıksa çalışır
if st.button("📡 Piyasayı Şimdi Tara") or otomatik_tarama:
    with st.spinner("Piyasa taranıyor, devasa hacim giren hisseler aranıyor..."):
        try:
            screener = Overview()
            
            # Arka plan filtreleri
            filters_dict = {
                'Exchange': 'NASDAQ',
                'Price': fiyat_secimi,
                'Current Volume': hacim_secimi,
                'Relative Volume': 'Over 2', # Normalden en az 2 kat fazla hacim
                'Performance': 'Today Up'    # Yükselişte olanlar
            }
            
            screener.set_filter(filters_dict=filters_dict)
            df = screener.screener_view()
            
            if not df.empty:
                gosterilecek_df = df[['Ticker', 'Company', 'Price', 'Change', 'Volume']].copy()
                gosterilecek_df.columns = ['Hisse Kodu', 'Şirket Adı', 'Anlık Fiyat', 'Günlük Yükseliş', 'İşlem Hacmi']
                
                su_an = datetime.now().strftime("%H:%M:%S")
                gosterilecek_df['Sinyal Saati'] = su_an
                
                st.success(f"[{su_an}] Tebrikler! Belirlediğin şartlara uyan {len(gosterilecek_df)} hisse bulundu. 🎯")
                st.dataframe(gosterilecek_df, use_container_width=True)
                
                # Sadece yeni bildirim atmak için saati kontrol edebilirsin ama şimdilik her taramada atacak
                for index, row in gosterilecek_df.iterrows():
                    mesaj = (f"🚨 YENİ SİNYAL: #{row['Hisse Kodu']}\n"
                             f"Şirket: {row['Şirket Adı']}\n"
                             f"Fiyat: ${row['Anlık Fiyat']}\n"
                             f"Yükseliş: {row['Günlük Yükseliş']}\n"
                             f"Saat: {row['Sinyal Saati']}")
                    send_telegram_message(mesaj)
                    time.sleep(0.5) # Telegram API'yi yormamak için
            else:
                su_an = datetime.now().strftime("%H:%M:%S")
                st.info(f"[{su_an}] Şu anki piyasa durumunda bu şartları sağlayan hisse bulunamadı.")
                
        except Exception as e:
            st.error("Sistem bir engele takıldı, sonraki döngüde tekrar denenecek.")

    # EĞER OTOMATİK TARAMA AÇIKSA: Sayfayı bekletip yeniden başlat
    if otomatik_tarama:
        st.warning(f"⏳ Otomatik mod aktif. Web sayfası {bekleme_suresi} dakika sonra kendi kendini yenileyip tekrar tarayacak. Lütfen bu sekmeyi kapatmayın...")
        time.sleep(bekleme_suresi * 60)
        st.rerun() # Sayfayı kodun en başından tekrar çalıştırır