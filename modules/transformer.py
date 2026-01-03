# modules/transformer.py

import streamlit as st
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def run():
    st.subheader("🔧 Data Transformation")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    # --- Temp State for Persistence ---
    # Create a temporary dataframe in session state to hold changes before saving
    if "transformer_temp_df" not in st.session_state:
        st.session_state["transformer_temp_df"] = st.session_state["data"].copy()

    df_temp = st.session_state["transformer_temp_df"]

    st.write("### 📊 Data Transformation View")
    st.dataframe(df_temp.head())

    st.write("### Select Transformation Operation")
    islem = st.selectbox("Operation", [
        "Label Encoding",
        "One-Hot Encoding",
        "Standard Scaling",
        "Min-Max Scaling",
        "Data Type Conversion",
        "Extract Date Columns"
    ])

    match islem:
        case "Label Encoding":
            kat_sutun = st.selectbox("Select Categorical Column", df_temp.select_dtypes(include='object').columns)
            if st.button("Apply Label Encoding"):
                try:
                    encoder = LabelEncoder()
                    # Convert to string to handle mixed types safely
                    df_temp[kat_sutun] = encoder.fit_transform(df_temp[kat_sutun].astype(str))
                    st.session_state["transformer_temp_df"] = df_temp
                    st.success("Label encoding applied temporarily.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        case "One-Hot Encoding":
            kat_sutun = st.multiselect(
                "Select column(s) for One-Hot Encoding",
                df_temp.select_dtypes(include='object').columns
            )

            if kat_sutun and st.button("Apply One-Hot Encoding"):
                try:
                    encoder = OneHotEncoder(sparse_output=False, drop='first')
                    encoded_array = encoder.fit_transform(df_temp[kat_sutun])
                    encoded_df = pd.DataFrame(
                        encoded_array,
                        columns=encoder.get_feature_names_out(kat_sutun),
                        index=df_temp.index
                    )
                    # Remove original columns and add encoded columns
                    df_temp = pd.concat([df_temp.drop(columns=kat_sutun), encoded_df], axis=1)
                    
                    st.session_state["transformer_temp_df"] = df_temp
                    st.success("One-hot encoding applied temporarily.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error applying One-Hot Encoding: {e}")

        case "Standard Scaling":
            sayisal_sutun = st.multiselect("Select column(s) for Standard Scaling", df_temp.select_dtypes(include='number').columns)
            if st.button("Apply Standard Scaler"):
                try:
                    scaler = StandardScaler()
                    df_temp[sayisal_sutun] = scaler.fit_transform(df_temp[sayisal_sutun])
                    st.session_state["transformer_temp_df"] = df_temp
                    st.success("Standard scaling applied temporarily.")
                    st.rerun()
                except Exception as e:
                     st.error(f"Error: {e}")

        case "Min-Max Scaling":
            sayisal_sutun = st.multiselect("Select column(s) for Min-Max Scaling", df_temp.select_dtypes(include='number').columns)
            if st.button("Apply Min-Max Scaler"):
                try:
                    scaler = MinMaxScaler()
                    df_temp[sayisal_sutun] = scaler.fit_transform(df_temp[sayisal_sutun])
                    st.session_state["transformer_temp_df"] = df_temp
                    st.success("Min-Max scaling applied temporarily.")
                    st.rerun()
                except Exception as e:
                     st.error(f"Error: {e}")

        case "Data Type Conversion":
            secilen_sutun = st.selectbox("Column to Convert", df_temp.columns)
            yeni_tip = st.selectbox("New Data Type", ["int", "float", "str"])
            if st.button("Convert Type"):
                try:
                    df_temp[secilen_sutun] = df_temp[secilen_sutun].astype(yeni_tip)
                    st.session_state["transformer_temp_df"] = df_temp
                    st.success(f"Column '{secilen_sutun}' converted to {yeni_tip} temporarily.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        case "Extract Date Columns":
            # DatetimeIndex check
            if not isinstance(df_temp.index, pd.DatetimeIndex):
                st.error("⛔ Data is not a time series or missing datetime index. Please load data with a datetime index.")
            else:
                if st.button("Extract Date Fields"):
                    try:
                        df_temp["Year"] = df_temp.index.year
                        df_temp["Month"] = df_temp.index.month
                        df_temp["Day"] = df_temp.index.day
                        df_temp["WeekdayNumber"] = df_temp.index.weekday + 1
                        
                        # Add day name
                        days = {
                            1: "Monday",
                            2: "Tuesday",
                            3: "Wednesday",
                            4: "Thursday",
                            5: "Friday",
                            6: "Saturday",
                            7: "Sunday"
                        }
                        df_temp["WeekdayName"] = df_temp["WeekdayNumber"].map(days)
                        
                        st.session_state["transformer_temp_df"] = df_temp
                        st.success("Date components extracted temporarily.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ------------------- Save Session State -------------------
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save to Session State"):
            st.session_state["data"] = st.session_state["transformer_temp_df"]
            # Clean up temp
            del st.session_state["transformer_temp_df"]
            st.success("Updated data saved to session_state.")
            st.rerun()

    with col2:
        if st.button("❌ Reset Changes"):
            del st.session_state["transformer_temp_df"]
            st.warning("All temporary changes reset.")
            st.rerun()
