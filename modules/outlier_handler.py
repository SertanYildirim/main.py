# modules/outlier_handler.py

import streamlit as st
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.cluster import DBSCAN
from scipy import stats

def run():
    st.subheader("🚨 Outlier Handling")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"]

    # --- Temp State for Persistence ---
    # Create a temporary dataframe in session state to hold changes before saving
    if "outlier_temp_df" not in st.session_state:
        st.session_state["outlier_temp_df"] = df.copy()
    
    df_temp = st.session_state["outlier_temp_df"]

    st.write("📊 Current Data (Temporary View):")
    st.dataframe(df_temp.head())

    # Numeric column selection
    numeric_columns = df_temp.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_columns) == 0:
        st.warning("No numeric columns found in the dataset.")
        return

    column = st.selectbox("Select numeric column", numeric_columns)

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "Outlier Analysis with IQR",
        "Outlier Analysis with Z-Score",
        "Outlier Analysis with DBSCAN"
    ])

    # Initialize variables to avoid 'undefined' errors
    outliers_iqr = pd.DataFrame()
    outliers_z = pd.DataFrame()
    outliers_db = pd.DataFrame()

    # -------------------- IQR --------------------
    with tab1:
        Q1 = df_temp[column].quantile(0.25)
        Q3 = df_temp[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers_iqr = df_temp[(df_temp[column] < lower_bound) | (df_temp[column] > upper_bound)]
        st.write("### Outliers (IQR):")
        st.dataframe(outliers_iqr)

    # -------------------- Z-SCORE --------------------
    with tab2:
        # Handling NaNs for Z-score calculation
        col_data = df_temp[column].dropna()
        if not col_data.empty:
            z_scores = np.abs(stats.zscore(col_data))
            threshold = 3
            # Filter based on index
            outlier_indices = col_data[z_scores > threshold].index
            outliers_z = df_temp.loc[outlier_indices]
            st.write("### Outliers (Z-Score):")
            st.dataframe(outliers_z)
        else:
            st.info("Column is empty or contains only NaNs.")

    # -------------------- DBSCAN --------------------
    with tab3:
        eps_val = st.slider("eps (neighborhood distance)", 0.1, 10.0, 1.5)
        min_samples_val = st.slider("min_samples", 1, 20, 5)

        # Missing value check
        if df_temp[column].isnull().any():
            st.error("⚠️ Missing values found in this column! DBSCAN does not work with NaN values.")
            if st.button("🧼 Go to Missing Data Handling"):
                st.session_state.page_selected = "Missing Data Handling"
                st.rerun()
        else:
            db = DBSCAN(eps=eps_val, min_samples=min_samples_val).fit(df_temp[[column]])
            labels = pd.Series(db.labels_, index=df_temp.index)
            outliers_db = df_temp.loc[labels[labels == -1].index]

            st.write("### Outliers (DBSCAN):")
            st.dataframe(outliers_db)

    # -------------------- Operation Options --------------------
    st.markdown("---")
    st.write("### 🔹 Handle Outliers")
    
    # User must select which method's outliers to target
    method = st.selectbox("Select Method to Target Outliers", ["IQR", "Z-Score", "DBSCAN"])
    
    if method == "IQR":
        target_outliers = outliers_iqr
    elif method == "Z-Score":
        target_outliers = outliers_z
    else:
        target_outliers = outliers_db

    if not target_outliers.empty:
        st.write(f"**{len(target_outliers)}** outliers detected using **{method}**.")
        
        action = st.selectbox(
            "Action Type",
            ["Drop", "Fill (Missing Data Methods)"]
        )

        # Drop Action
        if action == "Drop":
            if st.button("Drop Outliers"):
                st.session_state["outlier_temp_df"] = df_temp.drop(target_outliers.index)
                st.success("Outliers dropped temporarily ✅")
                st.rerun()

        # Fill Action
        elif action == "Fill (Missing Data Methods)":
            doldurma_yontemi = st.selectbox("Select Filling Method",
                ["ffill", "bfill", "Mean", "Median", "Mode", "Constant Value", "AI (KNNImputer)"]
            )

            # Different filling methods
            # We use a nested button structure via session state logic implied above
            apply_fill = False
            
            if doldurma_yontemi == "Constant Value":
                sabit_deger = st.text_input("Enter constant value", key="txt_sabit")
                if st.button("Fill with Constant Value", key="btn_fill_const"):
                    df_temp.loc[target_outliers.index, column] = np.nan
                    st.session_state["outlier_temp_df"] = df_temp.fillna(sabit_deger)
                    st.success("Filled with constant value temporarily ✅")
                    st.rerun()
            
            elif doldurma_yontemi == "AI (KNNImputer)":
                 if st.button("Fill with KNN", key="btn_fill_knn"):
                    if len(numeric_columns) == 0:
                        st.warning("KNNImputer works only on numeric columns ⚠️")
                    else:
                        df_temp.loc[target_outliers.index, column] = np.nan
                        imputer = KNNImputer(n_neighbors=3)
                        df_temp[numeric_columns] = imputer.fit_transform(df_temp[numeric_columns])
                        st.session_state["outlier_temp_df"] = df_temp
                        st.success("Filled with KNN Imputer temporarily ✅")
                        st.rerun()
            
            else:
                if st.button(f"Fill with {doldurma_yontemi}", key="btn_fill_generic"):
                    # First set outliers to NaN
                    df_temp.loc[target_outliers.index, column] = np.nan
                    
                    if doldurma_yontemi in ["ffill", "bfill"]:
                        st.session_state["outlier_temp_df"] = df_temp.fillna(method=doldurma_yontemi)
                    elif doldurma_yontemi == "Mean":
                        df_temp[column].fillna(df_temp[column].mean(), inplace=True)
                        st.session_state["outlier_temp_df"] = df_temp
                    elif doldurma_yontemi == "Median":
                        df_temp[column].fillna(df_temp[column].median(), inplace=True)
                        st.session_state["outlier_temp_df"] = df_temp
                    elif doldurma_yontemi == "Mode":
                        mode_val = df_temp[column].mode()[0]
                        df_temp[column].fillna(mode_val, inplace=True)
                        st.session_state["outlier_temp_df"] = df_temp
                    
                    st.success(f"Filled with {doldurma_yontemi} temporarily ✅")
                    st.rerun()

    else:
        st.info(f"No outliers found using {method}.")

    # ------------------- Save Session State -------------------
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save to Session State"):
            st.session_state["data"] = st.session_state["outlier_temp_df"]
            # Reset temp to reflect saved state
            del st.session_state["outlier_temp_df"]
            st.success("Updated data saved to session_state.")
            st.rerun()
            
    with col2:
        if st.button("❌ Reset Changes"):
            del st.session_state["outlier_temp_df"]
            st.warning("All temporary changes reset.")
            st.rerun()
