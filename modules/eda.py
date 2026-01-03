# modules/eda.py

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Function to detect data type based on content
def detect_dataset_content(df: pd.DataFrame) -> str:
    """
    Estimates the dataset type based on the content of the DataFrame.
    """
    # 1. Time series check
    if isinstance(df.index, pd.DatetimeIndex):
        return "⏳ Time Series Dataset"

    # 2. Numerical dataset
    num_cols = df.select_dtypes(include="number").shape[1]
    if num_cols / df.shape[1] > 0.7:
        return "🔢 Numerical Dataset"

    # 3. Categorical dataset
    cat_cols = df.select_dtypes(include="object").shape[1]
    if cat_cols / df.shape[1] > 0.5:
        return "🗂️ Categorical Dataset"

    # 4. Text data
    for col in df.select_dtypes(include="object"):
        if df[col].astype(str).str.len().mean() > 30:  # average string length
            return "📄 Text-Based Dataset"

    # 5. Geospatial data
    lower_cols = [col.lower() for col in df.columns]
    if ("latitude" in lower_cols or "lat" in lower_cols) and ("longitude" in lower_cols or "lon" in lower_cols):
        return "🌍 Geospatial Dataset"

    return "📊 General Purpose Tabular Dataset"


def run():
    st.subheader("📊 Exploratory Data Analysis (EDA)")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"]

    # Data type estimation
    dataset_type = detect_dataset_content(df)
    st.info(f"📌 This dataset is likely: **{dataset_type}**")

    # General Data Information
    st.write("### 🔍 General Data Information")
    st.write(f"**Rows:** {df.shape[0]}  \n**Columns:** {df.shape[1]}")
    st.dataframe(df.head())

    # Data Types
    st.write("### 📌 Data Types")
    st.dataframe(df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Data Type"}))

    st.write("### 📈 Numerical Variables")
    sayisal_sutunlar = df.select_dtypes(include="number").columns
    st.write(sayisal_sutunlar.tolist())

    st.write("### 📋 Categorical Variables")
    kategorik_sutunlar = df.select_dtypes(include="object").columns
    st.write(kategorik_sutunlar.tolist())

    # Basic Statistics
    st.write("### 📊 Basic Statistics")
    st.dataframe(df.describe().T)

    if len(sayisal_sutunlar) >= 2:
        st.write("### 🔥 Correlation Matrix (Heatmap)")

        fig, ax = plt.subplots()
        sns.heatmap(df[sayisal_sutunlar].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)
