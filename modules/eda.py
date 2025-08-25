# modules/eda.py

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# İçeriğe göre veri türünü bulma fonksiyonu
def detect_dataset_content(df: pd.DataFrame) -> str:
    """
    DataFrame'in içeriğine göre veri seti türünü tahmin eder.
    """
    # 1. Zaman serisi kontrolü
    if isinstance(df.index, pd.DatetimeIndex):
        return "⏳ Zaman Serisi Veri Seti"

    # 2. Sayısal veri seti
    num_cols = df.select_dtypes(include="number").shape[1]
    if num_cols / df.shape[1] > 0.7:
        return "🔢 Sayısal Veri Seti"

    # 3. Kategorik veri seti
    cat_cols = df.select_dtypes(include="object").shape[1]
    if cat_cols / df.shape[1] > 0.5:
        return "🗂️ Kategorik Veri Seti"

    # 4. Metin verisi
    for col in df.select_dtypes(include="object"):
        if df[col].astype(str).str.len().mean() > 30:  # ortalama string uzunluğu
            return "📄 Metin Tabanlı Veri Seti"

    # 5. Konumsal veri
    lower_cols = [col.lower() for col in df.columns]
    if ("latitude" in lower_cols or "lat" in lower_cols) and ("longitude" in lower_cols or "lon" in lower_cols):
        return "🌍 Konumsal Veri Seti"

    return "📊 Genel Amaçlı Tablo Veri Seti"


def run():
    st.subheader("📊 Keşifsel Veri Analizi (EDA)")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"]

    # Veri türü tahmini
    dataset_type = detect_dataset_content(df)
    st.info(f"📌 Bu veri seti büyük ihtimalle: **{dataset_type}**")

    # Veri genel bilgisi
    st.write("### 🔍 Veri Genel Bilgisi")
    st.write(f"**Satır sayısı:** {df.shape[0]}  \n**Sütun sayısı:** {df.shape[1]}")
    st.dataframe(df.head())

    # Veri tipi türleri
    st.write("### 📌 Veri Türleri")
    st.dataframe(df.dtypes.reset_index().rename(columns={"index": "Sütun", 0: "Veri Tipi"}))

    st.write("### 📈 Sayısal Değişkenler")
    sayisal_sutunlar = df.select_dtypes(include="number").columns
    st.write(sayisal_sutunlar.tolist())

    st.write("### 📋 Kategorik Değişkenler")
    kategorik_sutunlar = df.select_dtypes(include="object").columns
    st.write(kategorik_sutunlar.tolist())

    # Temel istatistikler
    st.write("### 📊 Temel İstatistikler")
    st.dataframe(df.describe().T)

    if len(sayisal_sutunlar) >= 2:
        st.write("### 🔥 Korelasyon Matrisi (Isı Haritası)")

        fig, ax = plt.subplots()
        sns.heatmap(df[sayisal_sutunlar].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)
