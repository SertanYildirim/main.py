# modules/merger.py

import streamlit as st
import pandas as pd

def run():
    st.subheader("🔗 Data Merging")

    if "data" not in st.session_state:
        st.warning("Please load the main data first.")
        return

    df1 = st.session_state["data"]
    st.write("📄 Main Data:")
    st.dataframe(df1.head())

    st.write("### ➕ Upload Second Dataset")
    file = st.file_uploader("Choose a CSV file", type=["csv"])

    if file:
        df2 = pd.read_csv(file)
        st.write("📄 Second Dataset Loaded:")
        st.dataframe(df2.head())

        ortak_sutun1 = st.selectbox("Column to match in Main Data", df1.columns)
        ortak_sutun2 = st.selectbox("Column to match in Second Data", df2.columns)

        merge_type = st.selectbox("Merge Type", ["inner", "left", "right", "outer"])

        if st.button("Merge Data"):
            try:
                merged_df = pd.merge(df1, df2, how=merge_type, left_on=ortak_sutun1, right_on=ortak_sutun2)
                st.session_state["data"] = merged_df
                st.success("Data merged successfully!")
                st.dataframe(merged_df)
            except Exception as e:
                st.error(f"Error occurred: {e}")
