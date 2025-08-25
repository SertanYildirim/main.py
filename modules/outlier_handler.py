# modules/outlier_handler.py

import streamlit as st
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.cluster import DBSCAN
from scipy import stats

def run():
    st.subheader("🚨 Aykırı Değerleri İşleme (Outlier Handler)")

    if "data" not in st.session_state:
        st.warning("Lütfen önce bir veri yükleyin.")
        return

    df = st.session_state["data"]
    df_temp = df.copy()  # Geçici kopya, değişiklikler burada yapılacak
    st.write("📊 Mevcut Veri:")
    st.dataframe(df_temp.head())

    # Sayısal kolon seçimi
    numeric_columns = df_temp.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_columns) == 0:
        st.warning("Veri setinde sayısal sütun bulunmamaktadır.")
        return

    column = st.selectbox("Sayısal veri sütunu seç", numeric_columns)

    # Tablar
    tab1, tab2, tab3 = st.tabs([
        "IQR ile Aykırı Değer Analizi",
        "Z-Score ile Aykırı Değer Analizi",
        "DBSCAN ile Aykırı Değer Analizi"
    ])

    outliers = pd.DataFrame()

    # -------------------- IQR --------------------
    with tab1:
        Q1 = df_temp[column].quantile(0.25)
        Q3 = df_temp[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df_temp[(df_temp[column] < lower_bound) | (df_temp[column] > upper_bound)]
        st.write("### Aykırı Değerler (IQR):")
        st.dataframe(outliers)

    # -------------------- Z-SCORE --------------------
    with tab2:
        z_scores = np.abs(stats.zscore(df_temp[column]))
        threshold = 3
        outliers = df_temp[z_scores > threshold]
        st.write("### Aykırı Değerler (Z-Score):")
        st.dataframe(outliers)

    # -------------------- DBSCAN --------------------
    with tab3:
        eps_val = st.slider("eps (komşuluk mesafesi)", 0.1, 10.0, 1.5)
        min_samples_val = st.slider("min_samples", 1, 20, 5)

        # Eksik değer kontrolü
        if df_temp[column].isnull().any():
            st.error("⚠️ Bu sütunda eksik değerler bulundu! DBSCAN NaN değerlerle çalışmaz.")
            if st.button("🧼 Eksik Veri İşlemlerine Git"):
                st.session_state.page_selected = "Eksik Veri İşlemleri"
                st.rerun()
        else:
            db = DBSCAN(eps=eps_val, min_samples=min_samples_val).fit(df_temp[[column]])
            labels = pd.Series(db.labels_, index=df_temp.index)
            outliers = df_temp.loc[labels[labels == -1].index]

            st.write("### Aykırı Değerler (DBSCAN):")
            st.dataframe(outliers)

    # -------------------- İşlem Seçenekleri --------------------
    if not outliers.empty:
        st.write("### 🔹 Aykırı Değerlerle Ne Yapmak İstersiniz?")
        action = st.selectbox(
            "İşlem türü",
            ["Sil", "Doldur (Eksik Veri Yöntemleri)"]
        )

        # Silme işlemi (geçici)
        if action == "Sil":
            if st.button("Aykırı Değerleri Sil"):
                df_temp = df_temp.drop(outliers.index)
                st.success("Aykırı değerler geçici olarak silindi ✅")
                st.dataframe(df_temp)

        # Doldurma işlemleri (geçici)
        elif action == "Doldur (Eksik Veri Yöntemleri)":
            df_temp.loc[outliers.index, column] = np.nan

            doldurma_yontemi = st.selectbox("Doldurma Yöntemi Seç",
                ["ffill", "bfill", "Ortalama", "Medyan", "Mod", "Sabit Değer", "Yapay Zeka (KNNImputer)"]
            )

            # Farklı doldurma yöntemleri
            if doldurma_yontemi in ["ffill", "bfill"]:
                if st.button("Doldur", key="btn_fill_fb"):
                    df_temp = df_temp.fillna(method=doldurma_yontemi)
                    st.success(f"{doldurma_yontemi.upper()} ile doldurma geçici olarak tamamlandı ✅")
                    st.dataframe(df_temp)

            elif doldurma_yontemi == "Ortalama":
                if st.button("Ortalama ile Doldur", key="btn_fill_mean"):
                    for col in numeric_columns:
                        df_temp[col].fillna(df_temp[col].mean(), inplace=True)
                    st.success("Ortalama ile doldurma geçici olarak tamamlandı ✅")
                    st.dataframe(df_temp)

            elif doldurma_yontemi == "Medyan":
                if st.button("Medyan ile Doldur", key="btn_fill_median"):
                    for col in numeric_columns:
                        df_temp[col].fillna(df_temp[col].median(), inplace=True)
                    st.success("Medyan ile doldurma geçici olarak tamamlandı ✅")
                    st.dataframe(df_temp)

            elif doldurma_yontemi == "Mod":
                if st.button("Mod ile Doldur", key="btn_fill_mode"):
                    for col in df_temp.columns:
                        if df_temp[col].isnull().any():
                            try:
                                mode_val = df_temp[col].mode()[0]
                                df_temp[col].fillna(mode_val, inplace=True)
                            except IndexError:
                                pass
                    st.success("Mod ile doldurma geçici olarak tamamlandı ✅")
                    st.dataframe(df_temp)

            elif doldurma_yontemi == "Sabit Değer":
                sabit_deger = st.text_input("Sabit değer girin", key="txt_sabit")
                if st.button("Sabit Değer ile Doldur", key="btn_fill_const"):
                    df_temp = df_temp.fillna(sabit_deger)
                    st.success("Sabit değer ile doldurma geçici olarak tamamlandı ✅")
                    st.dataframe(df_temp)

            elif doldurma_yontemi == "Yapay Zeka (KNNImputer)":
                if len(numeric_columns) == 0:
                    st.warning("KNNImputer sadece sayısal sütunlarda çalışır ⚠️")
                else:
                    if st.button("KNN ile Doldur", key="btn_fill_knn"):
                        imputer = KNNImputer(n_neighbors=3)
                        df_temp[numeric_columns] = imputer.fit_transform(df_temp[numeric_columns])
                        st.success("KNN Imputer ile doldurma geçici olarak tamamlandı ✅")
                        st.dataframe(df_temp)

    # ------------------- Session State Kaydet -------------------
    if st.button("✅ Session State'e Kaydet"):
        st.session_state["data"] = df_temp
        st.success("Güncellenmiş veri session_state'e kaydedildi.")
