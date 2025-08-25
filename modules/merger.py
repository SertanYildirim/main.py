# modules/merger.py

import streamlit as st
import pandas as pd

def run():
    st.subheader("🔗 Veri Birleştirme (Merge)")

    if "data" not in st.session_state:
        st.warning("Lütfen önce ana veriyi yükleyin.")
        return

    df1 = st.session_state["data"]
    st.write("📄 Ana Veri:")
    st.dataframe(df1.head())

    st.write("### ➕ İkinci Veriyi Yükle")
    file = st.file_uploader("CSV dosyası seçin", type=["csv"])

    if file:
        df2 = pd.read_csv(file)
        st.write("📄 Yüklenen İkinci Veri:")
        st.dataframe(df2.head())

        ortak_sutun1 = st.selectbox("Ana verideki eşleştirilecek sütun", df1.columns)
        ortak_sutun2 = st.selectbox("İkinci verideki eşleştirilecek sütun", df2.columns)

        merge_type = st.selectbox("Birleştirme Türü", ["inner", "left", "right", "outer"])

        if st.button("Verileri Birleştir"):
            try:
                merged_df = pd.merge(df1, df2, how=merge_type, left_on=ortak_sutun1, right_on=ortak_sutun2)
                st.session_state["data"] = merged_df
                st.success("Veriler başarıyla birleştirildi!")
                st.dataframe(merged_df)
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
