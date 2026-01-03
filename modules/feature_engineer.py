# modules/feature_engineer.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
import streamlit as st

def run():
    """
    Applies feature engineering steps.
    Works automatically on index if Loader found a date column (DatetimeIndex).
    Other steps are applied only if selected by the user.
    """

    st.subheader("📊 Feature Engineering")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"].copy()

    # --- 1) Categorical (One-Hot) ---
    st.write("### 🗂 Categorical Columns (One-Hot Encoding)")
    categorical_columns = st.multiselect(
        "Select categorical columns for One-Hot Encoding",
        df.select_dtypes(include="object").columns.tolist()
    )

    # --- 2) Numerical (Scaling) ---
    st.write("### 🔢 Numerical Columns (Min-Max Scaling)")
    scale_columns = st.multiselect(
        "Select numerical columns to scale",
        df.select_dtypes(include=np.number).columns.tolist()
    )

    # --- 3) Date (Button instead of automatic) ---
    st.write("### 📅 Date Features")
    has_dt_index = isinstance(df.index, pd.DatetimeIndex)

    if has_dt_index:
        st.caption("✅ DatetimeIndex detected; you can extract year/month/day/weekday features.")
        if st.button("📌 Extract Date Columns"):
            try:
                ts = df.index
                df["Year"] = ts.year
                df["Month"] = ts.month
                df["Day"] = ts.day
                df["Weekday"] = df.index.weekday + 1   # Monday=1, Sunday=7

                days = {
                    1: "Monday",
                    2: "Tuesday",
                    3: "Wednesday",
                    4: "Thursday",
                    5: "Friday",
                    6: "Saturday",
                    7: "Sunday"
                }
                df["WeekdayName"] = df["Weekday"].map(days)
                st.success("Year, Month, Day, Weekday features created from Index (DatetimeIndex).")
                
                if st.button("Save to Session State", key="save_date_features"):
                    st.session_state["data"] = df
                    st.success("Updated data saved to session_state.")
            except Exception as e:
                st.error(f"Error processing DatetimeIndex: {e}")
    else:
        st.info("ℹ️ No date column found (DatetimeIndex not detected).")

    st.write("### 📊 Feature Engineering Result Data")
    st.dataframe(df)

    # --- 4) New Feature Expressions ---
    st.write("### ✨ New Features (Optional)")
    new_features_input = st.text_area("Enter new feature expressions (e.g., df['new_col'] = df['col1'] + df['col2'])")

    if st.button("Apply Feature Engineering"):
        # 1. Categorical
        if categorical_columns:
            for column in categorical_columns:
                try:
                    encoder = OneHotEncoder(drop='first', sparse_output=False)  # scikit-learn >=1.2
                    one_hot_encoded = encoder.fit_transform(df[[column]])
                    one_hot_df = pd.DataFrame(
                        one_hot_encoded,
                        columns=encoder.get_feature_names_out([column]),
                        index=df.index
                    )
                    df = pd.concat([df, one_hot_df], axis=1)
                    df.drop(columns=[column], inplace=True)
                    st.success(f"Column '{column}' transformed with one-hot encoding.")
                except TypeError:
                    # Fallback for older scikit-learn versions
                    try:
                        encoder = OneHotEncoder(drop='first', sparse=False)
                        one_hot_encoded = encoder.fit_transform(df[[column]])
                        one_hot_df = pd.DataFrame(
                            one_hot_encoded,
                            columns=encoder.get_feature_names_out([column]),
                            index=df.index
                        )
                        df = pd.concat([df, one_hot_df], axis=1)
                        df.drop(columns=[column], inplace=True)
                        st.success(f"Column '{column}' transformed with one-hot encoding. (compat mode)")
                    except Exception as e:
                        st.error(f"Error transforming column '{column}': {e}")
                except Exception as e:
                    st.error(f"Error transforming column '{column}': {e}")
        else:
            st.info("No categorical columns selected for transformation.")

        # 2. Numerical
        if scale_columns:
            try:
                scaler = MinMaxScaler()
                df[scale_columns] = scaler.fit_transform(df[scale_columns])
                st.success(f"Numerical columns scaled: {', '.join(scale_columns)}")
            except Exception as e:
                st.error(f"Error scaling numerical columns: {e}")
        else:
            st.info("No numerical columns selected for scaling.")

        # 3. New Features
        if new_features_input.strip():
            try:
                # Expose df/np/pd objects explicitly to the user
                exec(new_features_input, {"df": df, "np": np, "pd": pd})
                st.success("New feature expressions applied successfully.")
            except Exception as e:
                st.error(f"Error applying new feature: {e}")

        # Show Results
        st.write("### 📊 Feature Engineering Result Data")
        st.dataframe(df)

        # Optional Save
        if st.button("Save to Session State", key="save_final_features"):
            st.session_state["data"] = df
            st.success("Updated data saved to session_state.")
