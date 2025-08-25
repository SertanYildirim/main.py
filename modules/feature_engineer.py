# modules/feature_engineer.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
import streamlit as st

def run():
    """
    Özellik mühendisliği adımlarını uygular.
    Loader tarih kolonu bulduysa index (DatetimeIndex) üzerinden otomatik çalışır.
    Diğer adımlar yalnızca kullanıcı seçim yaparsa uygulanır.
    """

    st.subheader("📊 Özellik Mühendisliği (Feature Engineering)")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"].copy()

    # --- 1) Kategorik (One-Hot) ---
    st.write("### 🗂 Kategorik Sütunlar (One-Hot Encoding)")
    categorical_columns = st.multiselect(
        "One-Hot Encoding yapılacak kategorik sütunları seçin",
        df.select_dtypes(include="object").columns.tolist()
    )

    # --- 2) Sayısal (Scaling) ---
    st.write("### 🔢 Sayısal Sütunlar (Min-Max Scaling)")
    scale_columns = st.multiselect(
        "Ölçeklenecek sayısal sütunları seçin",
        df.select_dtypes(include=np.number).columns.tolist()
    )

    # --- 3) Tarih (Otomatik yerine butonla) ---
    st.write("### 📅 Tarih Özellikleri")
    has_dt_index = isinstance(df.index, pd.DatetimeIndex)

    if has_dt_index:
        st.caption("✅ DatetimeIndex algılandı; isterseniz yıl/ay/gün/hafta_günü özelliklerine ayırabilirsiniz.")
        if st.button("📌 Tarih kolonlarını ayır"):
            try:
                ts = df.index
                df["Yıl"] = ts.year
                df["Ay"] = ts.month
                df["Gün"] = ts.day
                df["HaftaGünü"] = df.index.weekday + 1   # Pazartesi=1, Pazar=7

                gunler = {
                    1: "Pazartesi",
                    2: "Salı",
                    3: "Çarşamba",
                    4: "Perşembe",
                    5: "Cuma",
                    6: "Cumartesi",
                    7: "Pazar"
                }
                df["HaftaGünüAdı"] = df["HaftaGünü"].map(gunler)
                st.success("Index (DatetimeIndex) üzerinden yıl, ay, gün, hafta_günü özellikleri oluşturuldu.")
                if st.button("Session State'e Kaydet"):
                    st.session_state["data"] = df
                    st.success("Güncellenmiş veri session_state'e kaydedildi.")
            except Exception as e:
                st.error(f"DatetimeIndex işlenirken hata: {e}")
    else:
        st.info("ℹ️ Bu veride tarih kolonu yok (DatetimeIndex bulunamadı).")

    st.write("### 📊 Özellik Mühendisliği Sonuç Verisi")
    st.dataframe(df)

    # --- 4) Yeni Özellik İfadeleri ---
    st.write("### ✨ Yeni Özellikler (Opsiyonel)")
    new_features_input = st.text_area("Yeni feature ifadelerini yazın (örn: df['new_col'] = df['col1'] + df['col2'])")

    if st.button("Özellik Mühendisliğini Uygula"):
        # 1. Kategorik
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
                    st.success(f"'{column}' sütunu one-hot encoding ile dönüştürüldü.")
                except TypeError:
                    # Eski scikit-learn sürümleri için geri dönüş
                    try:
                        encoder = OneHotEncoder(drop='first', sparse_output=False)
                        one_hot_encoded = encoder.fit_transform(df[[column]])
                        one_hot_df = pd.DataFrame(
                            one_hot_encoded,
                            columns=encoder.get_feature_names_out([column]),
                            index=df.index
                        )
                        df = pd.concat([df, one_hot_df], axis=1)
                        df.drop(columns=[column], inplace=True)
                        st.success(f"'{column}' sütunu one-hot encoding ile dönüştürüldü. (compat mod)")
                    except Exception as e:
                        st.error(f"'{column}' sütunu dönüştürülürken hata: {e}")
                except Exception as e:
                    st.error(f"'{column}' sütunu dönüştürülürken hata: {e}")
        else:
            st.info("Dönüştürülecek kategorik sütun seçilmedi.")

        # 2. Sayısal
        if scale_columns:
            try:
                scaler = MinMaxScaler()
                df[scale_columns] = scaler.fit_transform(df[scale_columns])
                st.success(f"Sayısal sütunlar ölçeklendi: {', '.join(scale_columns)}")
            except Exception as e:
                st.error(f"Sayısal sütunlar ölçeklenirken hata: {e}")
        else:
            st.info("Ölçeklenecek sayısal sütun seçilmedi.")

        # 3. Yeni Özellikler
        if new_features_input.strip():
            try:
                # Kullanıcıya açıkça df/np/pd objelerini sunuyoruz
                exec(new_features_input, {"df": df, "np": np, "pd": pd})
                st.success("Yeni feature ifadeleri başarıyla uygulandı.")
            except Exception as e:
                st.error(f"Yeni feature uygulanırken hata: {e}")

        # Sonuçları göster
        st.write("### 📊 Özellik Mühendisliği Sonuç Verisi")
        st.dataframe(df)

        # İsteğe bağlı kaydet
        if st.button("Session State'e Kaydet"):
            st.session_state["data"] = df
            st.success("Güncellenmiş veri session_state'e kaydedildi.")
