# modules/filter_sort_safe.py
import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.subheader("🔹 Veri Filtreleme ve Seçim (Geçici veya Session’a Kaydet)")

    if "data" not in st.session_state:
        st.warning("Lütfen önce bir veri yükleyin.")
        return

    # Ana DF ilk yüklenince yedekle
    if "data_original" not in st.session_state:
        st.session_state["data_original"] = st.session_state["data"].copy()

    original_df = st.session_state["data_original"]  # Yedek DF
    df = original_df.copy()

    # Temp storage
    if "num_filters_temp" not in st.session_state:
        st.session_state["num_filters_temp"] = {}
    if "cat_filters_temp" not in st.session_state:
        st.session_state["cat_filters_temp"] = {}

    num_filters = {}
    cat_filters = {}

    st.write("### ➕ Sayısal Sütunlar İçin Aralık Belirle")
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        if min_val != max_val:
            default_vals = st.session_state["num_filters_temp"].get(col, (min_val, max_val))
            selected_range = st.slider(f"{col} aralığını seçin", min_val, max_val, default_vals, key=f"num_{col}")
            num_filters[col] = selected_range
            st.session_state["num_filters_temp"][col] = selected_range

    st.write("### ➕ Kategorik Sütunlar İçin Seçim Yap")
    cat_cols = [c for c in df.select_dtypes(include="object").columns if df[c].nunique() <= 20]
    for col in cat_cols:
        options = df[col].unique().tolist()
        default_vals = st.session_state["cat_filters_temp"].get(col, options)
        selected_vals = st.multiselect(f"{col} için değer seçin", options, default=default_vals, key=f"cat_{col}")
        cat_filters[col] = selected_vals
        st.session_state["cat_filters_temp"][col] = selected_vals

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sorgulama Alanına Kaydet"):
            filtered_df = df.copy()
            # Sayısal filtre
            for col, (min_val, max_val) in num_filters.items():
                filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
            # Kategorik filtre
            for col, selected_vals in cat_filters.items():
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

            st.success(f"Geçici DF hazır. {len(filtered_df)} satır bulundu.")
            st.dataframe(filtered_df)
            st.session_state["temp_filtered"] = filtered_df  # Bu fonksiyon içinde kullanılabilir

    with col2:
        if st.button("Ana Projeye Kaydet"):
            filtered_df = df.copy()
            for col, (min_val, max_val) in num_filters.items():
                filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
            for col, selected_vals in cat_filters.items():
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

            st.session_state["data_filtered"] = filtered_df
            st.success("Filtrelenmiş DF session_state’e kaydedildi ve diğer modüllerde kullanılabilir.")

    # Sıfırlama butonu
    if st.button("Seçimleri Sıfırla"):
        # Temp filtreleri temizle
        st.session_state["num_filters_temp"] = {}
        st.session_state["cat_filters_temp"] = {}

        # Temp filtered DF'yi kaldır
        if "temp_filtered" in st.session_state:
            del st.session_state["temp_filtered"]

        # Ana session_state'deki filtrelenmiş DF'yi kaldır
        if "data_filtered" in st.session_state:
            del st.session_state["data_filtered"]

        # Ana DF'yi orijinal yedek DF'ye döndür
        st.session_state["data"] = st.session_state["data_original"].copy()

        st.success("Seçimler sıfırlandı, DF orijinal haline döndü.")
        st.rerun()
