import streamlit as st
import pandas as pd
from finvizfinance.screener.overview import Overview

st.set_page_config(page_title="NASDAQ Test", layout="wide")
st.title("🛠 Sistem Test Paneli")

if st.button("📡 Test Et ve Veri Çek"):
    try:
        st.write("Finviz tarayıcı başlatılıyor...")
        screener = Overview()
        
        st.write("Filtreler uygulanıyor...")
        # Çok basit bir filtre deneyelim
        filters = {'Exchange': 'NASDAQ', 'Price': 'Under $5'}
        screener.set_filter(filters_dict=filters)
        
        st.write("Veri çekiliyor...")
        df = screener.screener_view()
        
        if df is not None and not df.empty:
            st.success(f"Başarılı! {len(df)} adet hisse bulundu.")
            st.dataframe(df.head())
        else:
            st.warning("Veri çekildi ama sonuç boş döndü (Filtreler çok dar olabilir).")
            
    except Exception as e:
        st.error(f"DETAYLI HATA: {e}")
        st.write("Lütfen bu hata mesajını bana ilet.")
