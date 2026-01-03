# modules/filter_sort.py

import streamlit as st
import pandas as pd

def run():
    st.subheader("🔎 Filtering and Sorting")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"]
    df_temp = df.copy()  # Temporary copy, operations are performed here

    st.write("📊 Current Data (Temporary):")
    st.dataframe(df_temp.head())

    st.markdown("---")
    st.write("### 🔹 Filtering")

    filtre_sutun = st.selectbox("Select column to filter", df_temp.columns)

    if pd.api.types.is_numeric_dtype(df_temp[filtre_sutun]):
        min_val = float(df_temp[filtre_sutun].min())
        max_val = float(df_temp[filtre_sutun].max())
        
        # Streamlit slider throws an error if min == max
        if min_val == max_val:
            st.info(f"All values in this column are {min_val}. No range to filter.")
        else:
            val = st.slider("Select value range", min_val, max_val, (min_val, max_val))
            df_temp = df_temp[df_temp[filtre_sutun].between(val[0], val[1])]
            
    elif pd.api.types.is_datetime64_any_dtype(df_temp[filtre_sutun]):
        start_date = st.date_input("Start date", df_temp[filtre_sutun].min().date())
        end_date = st.date_input("End date", df_temp[filtre_sutun].max().date())
        df_temp = df_temp[(df_temp[filtre_sutun] >= pd.to_datetime(start_date)) &
                          (df_temp[filtre_sutun] <= pd.to_datetime(end_date))]
    else:
        unique_vals = df_temp[filtre_sutun].dropna().unique().tolist()
        selected_vals = st.multiselect("Select values to filter", unique_vals, default=unique_vals)
        df_temp = df_temp[df_temp[filtre_sutun].isin(selected_vals)]

    st.markdown("---")
    st.write("### 🔸 Sorting")

    sort_column = st.selectbox("Select column to sort", df_temp.columns)
    # Changed "Artan" to "Ascending" to match English UI
    ascending = st.radio("Sort order", ["Ascending", "Descending"]) == "Ascending"
    df_temp = df_temp.sort_values(by=sort_column, ascending=ascending)

    st.write("### 📊 Filtering and Sorting Result (Temporary)")
    st.dataframe(df_temp)

    # ------------------- Save Session State -------------------
    if st.button("✅ Save to Session State"):
        st.session_state["data"] = df_temp
        st.success("Updated data saved to session_state.")
