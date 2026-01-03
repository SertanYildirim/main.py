import streamlit as st
import pandas as pd
from sklearn.impute import KNNImputer

def run():
    st.subheader("🧼 Data Cleaning")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"].copy()

    st.write("### 📊 Overview of Missing Values")
    null_counts = df.isnull().sum()
    null_df = pd.DataFrame({
        "Column": null_counts.index,
        "Missing Values Count": null_counts.values
    })
    st.dataframe(null_df)

    st.write("## 🧹 Cleaning Operations")
    tab1, tab2 = st.tabs(["🗑️ Drop Missing Data", "✏️ Fill Missing Data"])

    # --- Tab 1: Drop Missing Data ---
    with tab1:
        st.markdown("You can drop missing data by **row** or **column**.")
        silme_yontemi = st.radio("Drop Method", ["Drop rows", "Drop columns"], key="silme_tab1")

        eksik_kolonlar = null_counts[null_counts > 0].index.tolist()
        secilen_kolon = st.multiselect("Select specific columns to drop from", eksik_kolonlar)

        if "temp_tab1" not in st.session_state:
            st.session_state["temp_tab1"] = df.copy()
            st.session_state["undo_tab1"] = []

        # --- Work only with existing columns ---
        valid_cols = [col for col in secilen_kolon if col in st.session_state["temp_tab1"].columns]

        disable_btn = False
        if valid_cols:
            has_missing = any(st.session_state["temp_tab1"][col].isnull().any() for col in valid_cols)
            if not has_missing:
                disable_btn = True
                st.warning("No missing data in selected columns, operation cannot be performed.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Drop", key="btn_sil_tab1", disabled=disable_btn):
                st.session_state["undo_tab1"].append(st.session_state["temp_tab1"].copy())

                if silme_yontemi == "Drop rows":
                    if valid_cols:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].dropna(subset=valid_cols)
                    else:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].dropna()
                else: # Drop columns
                    if valid_cols:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].drop(columns=valid_cols)
                    else:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].dropna(axis=1)

                st.success("Missing data dropped ✅")
                st.dataframe(st.session_state["temp_tab1"])

        with col2:
            if st.button("Undo", key="btn_undo_tab1") and st.session_state["undo_tab1"]:
                st.session_state["temp_tab1"] = st.session_state["undo_tab1"].pop()
                st.success("Last action undone ✅")
                st.dataframe(st.session_state["temp_tab1"])

        if st.button("Save to Main DF", key="save_tab1"):
            st.session_state["data"] = st.session_state["temp_tab1"]
            st.success("Changes in Tab 1 saved to main DF ✅")

    # --- Tab 2: Fill Missing Data ---
    with tab2:
        st.markdown("You can fill missing data using different strategies.")
        
        # English options mapping
        doldurma_yontemi = st.selectbox(
            "Filling Method",
            ["ffill", "bfill", "Mean", "Median", "Mode", "Constant Value", "AI (KNNImputer)"],
            key="doldurma_tab2"
        )

        sayisal_kolonlar = df.select_dtypes(include="number").columns
        eksik_sayisal = [col for col in sayisal_kolonlar if df[col].isnull().any()]
        secilen_kolon = st.multiselect("Select specific columns to fill", eksik_sayisal)

        if "temp_tab2" not in st.session_state:
            st.session_state["temp_tab2"] = df.copy()
            st.session_state["undo_tab2"] = []

        # --- Work only with existing numeric columns ---
        valid_cols = [col for col in secilen_kolon if col in st.session_state["temp_tab2"].columns]

        disable_btn = False
        if valid_cols:
            has_missing = any(st.session_state["temp_tab2"][col].isnull().any() for col in valid_cols)
            if not has_missing:
                disable_btn = True
                st.warning("No missing data in selected columns, operation cannot be performed.")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Fill", key="btn_fill_tab2", disabled=disable_btn):
                st.session_state["undo_tab2"].append(st.session_state["temp_tab2"].copy())
                df_filled = st.session_state["temp_tab2"].copy()

                if doldurma_yontemi in ["ffill", "bfill"]:
                    df_filled[valid_cols] = df_filled[valid_cols].fillna(method=doldurma_yontemi)
                elif doldurma_yontemi == "Mean":
                    for col in valid_cols:
                        df_filled[col].fillna(df_filled[col].mean(), inplace=True)
                elif doldurma_yontemi == "Median":
                    for col in valid_cols:
                        df_filled[col].fillna(df_filled[col].median(), inplace=True)
                elif doldurma_yontemi == "Mode":
                    for col in valid_cols:
                        df_filled[col].fillna(df_filled[col].mode()[0], inplace=True)
                elif doldurma_yontemi == "Constant Value":
                    sabit_deger = st.text_input("Enter constant value", key="txt_sabit_tab2")
                    # Note: You might need to cast 'sabit_deger' to float/int if columns are numeric
                    df_filled[valid_cols] = df_filled[valid_cols].fillna(sabit_deger)
                elif doldurma_yontemi == "AI (KNNImputer)":
                    imputer = KNNImputer(n_neighbors=3)
                    df_filled[valid_cols] = imputer.fit_transform(df_filled[valid_cols])

                st.session_state["temp_tab2"] = df_filled
                st.success("Missing data filled ✅")
                st.dataframe(df_filled)

        with col2:
            # Fixed variable name here: changed 'undo_tab2_stack' to 'undo_tab2'
            if st.button("Undo", key="btn_undo_tab2") and st.session_state.get("undo_tab2", []):
                st.session_state["temp_tab2"] = st.session_state["undo_tab2"].pop()
                st.success("Last action undone ✅")
                st.dataframe(st.session_state["temp_tab2"])

        with col3:
            if st.button("Save to Main DF", key="save_tab2"):
                st.session_state["data"] = st.session_state["temp_tab2"]
                st.success("Changes in Tab 2 saved to main DF ✅")
