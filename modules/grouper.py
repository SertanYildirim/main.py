# modules/grouper.py

import streamlit as st
import pandas as pd

def run():
    st.subheader("📊 Data Grouping (Grouper)")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"]
    
    st.write("📊 Current Data (Temporary):")
    st.dataframe(df.head())

    st.write("### ➕ Select Column to Group By")
    group_column = st.selectbox("Select column to group by", df.columns)

    st.write("### 🔸 Aggregation Function")
    aggregation_func = st.selectbox("Select function", ["mean", "sum", "count", "min", "max", "median"])

    # 1. Step: Perform Grouping
    if st.button("Group and Summarize"):
        try:
            # Get numerical columns, exclude the grouping column
            num_cols = [col for col in df.select_dtypes(include="number").columns if col != group_column]

            if not num_cols:
                st.warning("No numerical data found other than the selected column. Grouping requires numerical columns.")
            else:
                # Grouping and aggregation
                grouped_df = df.groupby(group_column)[num_cols].agg(aggregation_func).reset_index()

                # Rename columns
                grouped_df.columns = [group_column] + [f"{col}_{aggregation_func}" for col in num_cols]
                
                # Save to temporary state to allow viewing and saving in the next step
                st.session_state["grouped_temp"] = grouped_df

        except Exception as e:
            st.error(f"Error occurred: {e}")

    # 2. Step: Show Result and Save (Persistent Block)
    if "grouped_temp" in st.session_state:
        st.write("### 📊 Grouping Result (Temporary)")
        st.dataframe(st.session_state["grouped_temp"])

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✅ Save to Session State"):
                st.session_state["data"] = st.session_state["grouped_temp"]
                # Optional: Clear temp after save
                del st.session_state["grouped_temp"]
                st.success("Updated data saved to session_state.")
                st.rerun() # Refresh to show new data
        with col2:
            if st.button("❌ Clear Result"):
                del st.session_state["grouped_temp"]
                st.rerun()
