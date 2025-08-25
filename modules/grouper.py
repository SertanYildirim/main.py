# modules/grouper.py

import streamlit as st
import pandas as pd

def run():
    st.subheader("📊 Veriyi Gruplama (Grouper)")

    if "data" not in st.session_state:
        st.warning("Lütfen önce bir veri yükleyin.")
        return

    df = st.session_state["data"]
    df_temp = df.copy()  # Geçici DataFrame

    st.write("📊 Mevcut Veri (Geçici):")
    st.dataframe(df_temp.head())

    st.write("### ➕ Gruplama Yapılacak Kolonu Seç")
    group_column = st.selectbox("Gruplama yapılacak sütunu seç", df_temp.columns)

    st.write("### 🔸 Gruplama Sonrası Hangi İşlemi Yapmak İstersiniz?")
    aggregation_func = st.selectbox("Özetleme Fonksiyonu", ["mean", "sum", "count", "min", "max", "median"])

    if st.button("Grupla ve Özetle"):
        try:
            # Sayısal sütunları al, grup sütununu çıkar
            num_cols = [col for col in df_temp.select_dtypes(include="number").columns if col != group_column]

            if not num_cols:
                st.warning("Seçilen sütun dışında sayısal veri bulunamadı. Gruplama işlemi sayısal sütunlarla yapılır.")
                return

            # Gruplama ve aggregation
            grouped_df = df_temp.groupby(group_column)[num_cols].agg(aggregation_func).reset_index()

            # Yeni sütun isimleri
            grouped_df.columns = [group_column] + [f"{col}_{aggregation_func}" for col in num_cols]

            st.write("### 📊 Gruplama Sonucu (Geçici)")
            st.dataframe(grouped_df)

            # ------------------- Session State Kaydet -------------------
            if st.button("✅ Session State'e Kaydet"):
                st.session_state["data"] = grouped_df
                st.success("Güncellenmiş veri session_state'e kaydedildi.")

        except Exception as e:
            st.error(f"Hata oluştu: {e}")
