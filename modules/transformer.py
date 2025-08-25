# modules/transformer.py

import streamlit as st
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def run():
    st.subheader("🔧 Veri Dönüştürme")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"]
    df_temp = df.copy()  # Geçici kopya, işlemler burada yapılacak

    st.write("### 📊 Veri Dönüştürme Verisi")
    st.dataframe(df_temp)

    st.write("### Dönüştürme İşlemini Seçin")
    islem = st.selectbox("İşlem", [
        "Label Encoding",
        "One-Hot Encoding",
        "Standard Scaling",
        "Min-Max Scaling",
        "Veri Tipi Dönüştürme",
        "Tarih Sütunlarını Ayır"
    ])

    match islem:
        case "Label Encoding":
            kat_sutun = st.selectbox("Kategorik Sütun Seçin", df_temp.select_dtypes(include='object').columns)
            if st.button("Label Encode Et"):
                encoder = LabelEncoder()
                df_temp[kat_sutun] = encoder.fit_transform(df_temp[kat_sutun].astype(str))
                st.success("Label encoding geçici olarak uygulandı.")
                st.dataframe(df_temp)

        case "One-Hot Encoding":
            kat_sutun = st.multiselect(
                "One-Hot Encoding yapılacak sütun(lar)",
                df_temp.select_dtypes(include='object').columns
            )

            if kat_sutun and st.button("One-Hot Encode Et"):
                try:
                    encoder = OneHotEncoder(sparse_output=False, drop='first')
                    encoded_array = encoder.fit_transform(df_temp[kat_sutun])
                    encoded_df = pd.DataFrame(
                        encoded_array,
                        columns=encoder.get_feature_names_out(kat_sutun),
                        index=df_temp.index
                    )
                    # Orijinal sütunları kaldırıp encode edilmiş sütunları ekle
                    df_temp = pd.concat([df_temp.drop(columns=kat_sutun), encoded_df], axis=1)

                    st.success("One-hot encoding geçici olarak uygulandı.")
                    st.dataframe(df_temp)
                except Exception as e:
                    st.error(f"One-Hot Encoding uygulanırken hata: {e}")

        case "Standard Scaling":
            sayisal_sutun = st.multiselect("Standard Scaling yapılacak sütun(lar)", df_temp.select_dtypes(include='number').columns)
            if st.button("Standard Scaler Uygula"):
                scaler = StandardScaler()
                df_temp[sayisal_sutun] = scaler.fit_transform(df_temp[sayisal_sutun])
                st.success("Standard scaling geçici olarak uygulandı.")
                st.dataframe(df_temp)

        case "Min-Max Scaling":
            sayisal_sutun = st.multiselect("Min-Max Scaling yapılacak sütun(lar)", df_temp.select_dtypes(include='number').columns)
            if st.button("Min-Max Scaler Uygula"):
                scaler = MinMaxScaler()
                df_temp[sayisal_sutun] = scaler.fit_transform(df_temp[sayisal_sutun])
                st.success("Min-Max scaling geçici olarak uygulandı.")
                st.dataframe(df_temp)

        case "Veri Tipi Dönüştürme":
            secilen_sutun = st.selectbox("Dönüştürülecek sütun", df_temp.columns)
            yeni_tip = st.selectbox("Yeni veri tipi", ["int", "float", "str"])
            if st.button("Tip Dönüştür"):
                try:
                    df_temp[secilen_sutun] = df_temp[secilen_sutun].astype(yeni_tip)
                    st.success(f"{secilen_sutun} sütunu {yeni_tip} tipine geçici olarak dönüştürüldü.")
                    st.dataframe(df_temp)
                except Exception as e:
                    st.error(f"Hata: {e}")

        case "Tarih Sütunlarını Ayır":
            # DatetimeIndex kontrolü
            if not isinstance(df_temp.index, pd.DatetimeIndex):
                st.error(
                    "⛔ Veri zaman serisi değil veya datetime index yok. Lütfen datetime index içeren bir veri yükleyin.")
            else:
                if st.button("Tarih Alanlarını Ayır"):
                    try:
                        df_temp["year"] = df_temp.index.year
                        df_temp["month"] = df_temp.index.month
                        df_temp["day"] = df_temp.index.day
                        df_temp["HaftaGünüNumara"] = df_temp.index.weekday + 1
                        # Gün adı eklemek için
                        gunler = {1: "Pazartesi",2:"Salı",3:"Çarşamba",4:"Perşembe",5:"Cuma",6:"Cumartesi",7:"Pazar"}
                        df_temp["HaftaGünüAdı"] = df_temp["HaftaGünüNumara"].map(gunler)
                        st.success("Tarih bileşenleri geçici olarak ayrıldı.")
                        st.dataframe(df_temp)
                    except Exception as e:
                        st.error(f"Hata: {e}")

    # ------------------- Session State Kaydet -------------------
    if st.button("✅ Session State'e Kaydet"):
        st.session_state["data"] = df_temp
        st.success("Güncellenmiş veri session_state'e kaydedildi.")
