# modules/filter_sort_safe.py
import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.subheader("🔹 Data Filtering and Selection (Temporary or Save to Session)")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    # Backup main DF on first load
    if "data_original" not in st.session_state:
        st.session_state["data_original"] = st.session_state["data"].copy()

    original_df = st.session_state["data_original"]  # Backup DF
    df = original_df.copy()

    # Temp storage
    if "num_filters_temp" not in st.session_state:
        st.session_state["num_filters_temp"] = {}
    if "cat_filters_temp" not in st.session_state:
        st.session_state["cat_filters_temp"] = {}

    num_filters = {}
    cat_filters = {}

    st.write("### ➕ Set Range for Numerical Columns")
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        if min_val != max_val:
            default_vals = st.session_state["num_filters_temp"].get(col, (min_val, max_val))
            selected_range = st.slider(f"Select range for {col}", min_val, max_val, default_vals, key=f"num_{col}")
            num_filters[col] = selected_range
            st.session_state["num_filters_temp"][col] = selected_range

    st.write("### ➕ Make Selection for Categorical Columns")
    cat_cols = [c for c in df.select_dtypes(include="object").columns if df[c].nunique() <= 20]
    for col in cat_cols:
        options = df[col].unique().tolist()
        default_vals = st.session_state["cat_filters_temp"].get(col, options)
        selected_vals = st.multiselect(f"Select values for {col}", options, default=default_vals, key=f"cat_{col}")
        cat_filters[col] = selected_vals
        st.session_state["cat_filters_temp"][col] = selected_vals

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save to Query Area"):
            filtered_df = df.copy()
            # Numerical filter
            for col, (min_val, max_val) in num_filters.items():
                filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
            # Categorical filter
            for col, selected_vals in cat_filters.items():
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

            st.success(f"Temporary DF ready. {len(filtered_df)} rows found.")
            st.dataframe(filtered_df)
            st.session_state["temp_filtered"] = filtered_df  # Can be used within this function

    with col2:
        if st.button("Save to Main Project"):
            filtered_df = df.copy()
            for col, (min_val, max_val) in num_filters.items():
                filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
            for col, selected_vals in cat_filters.items():
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

            st.session_state["data_filtered"] = filtered_df
            st.success("Filtered DF saved to session_state and available for other modules.")

    # Reset button
    if st.button("Reset Selections"):
        # Clear temp filters
        st.session_state["num_filters_temp"] = {}
        st.session_state["cat_filters_temp"] = {}

        # Remove temp filtered DF
        if "temp_filtered" in st.session_state:
            del st.session_state["temp_filtered"]

        # Remove filtered DF from main session_state
        if "data_filtered" in st.session_state:
            del st.session_state["data_filtered"]

        # Revert main DF to original backup DF
        st.session_state["data"] = st.session_state["data_original"].copy()

        st.success("Selections reset, DF reverted to original state.")
        st.rerun()
