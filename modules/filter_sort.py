# modules/filter_sort.py

import streamlit as st
import pandas as pd


def run():
    st.subheader("🔎 Filtreleme ve Sıralama")

    if "data" not in st.session_state:
        st.warning("Lütfen önce bir veri yükleyin.")
        return

    df = st.session_state["data"]
    df_temp = df.copy()  # Geçici kopya, işlemler burada yapılacak

    st.write("📊 Mevcut Veri (Geçici):")
    st.dataframe(df_temp.head())

    st.markdown("---")
    st.write("### 🔹 Filtreleme")

    filtre_sutun = st.selectbox("Filtrelenecek sütunu seç", df_temp.columns)

    if pd.api.types.is_numeric_dtype(df_temp[filtre_sutun]):
        min_val = float(df_temp[filtre_sutun].min())
        max_val = float(df_temp[filtre_sutun].max())
        val = st.slider("Değer aralığını seç", min_val, max_val, (min_val, max_val))
        df_temp = df_temp[df_temp[filtre_sutun].between(val[0], val[1])]
    elif pd.api.types.is_datetime64_any_dtype(df_temp[filtre_sutun]):
        start_date = st.date_input("Başlangıç tarihi", df_temp[filtre_sutun].min().date())
        end_date = st.date_input("Bitiş tarihi", df_temp[filtre_sutun].max().date())
        df_temp = df_temp[(df_temp[filtre_sutun] >= pd.to_datetime(start_date)) &
                          (df_temp[filtre_sutun] <= pd.to_datetime(end_date))]
    else:
        unique_vals = df_temp[filtre_sutun].dropna().unique().tolist()
        selected_vals = st.multiselect("Filtrelemek istediğiniz değerleri seçin", unique_vals, default=unique_vals)
        df_temp = df_temp[df_temp[filtre_sutun].isin(selected_vals)]

    st.markdown("---")
    st.write("### 🔸 Sıralama")

    sort_column = st.selectbox("Sıralanacak sütunu seç", df_temp.columns)
    ascending = st.radio("Sıralama tipi", ["Artan", "Azalan"]) == "Artan"
    df_temp = df_temp.sort_values(by=sort_column, ascending=ascending)

    st.write("### 📊 Filtreleme ve Sıralama Sonucu (Geçici)")
    st.dataframe(df_temp)

    # ------------------- Session State Kaydet -------------------
    if st.button("✅ Session State'e Kaydet"):
        st.session_state["data"] = df_temp
        st.success("Güncellenmiş veri session_state'e kaydedildi.")
