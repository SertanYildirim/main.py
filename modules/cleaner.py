import streamlit as st
import pandas as pd
from sklearn.impute import KNNImputer


def run():
    st.subheader("🧼 Veri Temizleme")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"].copy()

    st.write("### 📊 Eksik Değerlerin Genel Görünümü")
    null_counts = df.isnull().sum()
    null_df = pd.DataFrame({
        "Sütun": null_counts.index,
        "Eksik Değer Sayısı": null_counts.values
    })
    st.dataframe(null_df)

    st.write("## 🧹 Temizleme İşlemleri")
    tab1, tab2 = st.tabs(["🗑️ Eksik Verileri Sil", "✏️ Eksik Verileri Doldur"])

    # --- Tab 1: Eksik Verileri Sil ---
    with tab1:
        st.markdown("Eksik verileri **satır** veya **sütun** bazında silebilirsiniz.")
        silme_yontemi = st.radio("Silme Yöntemi", ["Satır bazında sil", "Sütun bazında sil"], key="silme_tab1")

        eksik_kolonlar = null_counts[null_counts > 0].index.tolist()
        secilen_kolon = st.multiselect("Sadece seçili kolonları silmek için seçin", eksik_kolonlar)

        if "temp_tab1" not in st.session_state:
            st.session_state["temp_tab1"] = df.copy()
            st.session_state["undo_tab1"] = []

        # --- Sadece mevcut sütunlarla çalış ---
        valid_cols = [col for col in secilen_kolon if col in st.session_state["temp_tab1"].columns]

        disable_btn = False
        if valid_cols:
            has_missing = any(st.session_state["temp_tab1"][col].isnull().any() for col in valid_cols)
            if not has_missing:
                disable_btn = True
                st.warning("Seçilen kolonlarda eksik veri yok, silme işlemi yapılamaz.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sil", key="btn_sil_tab1", disabled=disable_btn):
                st.session_state["undo_tab1"].append(st.session_state["temp_tab1"].copy())

                if silme_yontemi == "Satır bazında sil":
                    if valid_cols:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].dropna(subset=valid_cols)
                    else:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].dropna()
                else:
                    if valid_cols:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].drop(columns=valid_cols)
                    else:
                        st.session_state["temp_tab1"] = st.session_state["temp_tab1"].dropna(axis=1)

                st.success("Eksik veriler silindi ✅")
                st.dataframe(st.session_state["temp_tab1"])

        with col2:
            if st.button("Geri Al", key="btn_undo_tab1") and st.session_state["undo_tab1"]:
                st.session_state["temp_tab1"] = st.session_state["undo_tab1"].pop()
                st.success("Son işlem geri alındı ✅")
                st.dataframe(st.session_state["temp_tab1"])

        if st.button("Ana DF'ye Kaydet", key="save_tab1"):
            st.session_state["data"] = st.session_state["temp_tab1"]
            st.success("Tab 1’deki değişiklikler ana DF’ye kaydedildi ✅")

    # --- Tab 2: Eksik Verileri Doldur ---
    with tab2:
        st.markdown("Eksik verileri farklı stratejilerle doldurabilirsiniz.")
        doldurma_yontemi = st.selectbox(
            "Doldurma Yöntemi",
            ["ffill", "bfill", "Ortalama", "Medyan", "Mod", "Sabit Değer", "Yapay Zeka (KNNImputer)"],
            key="doldurma_tab2"
        )

        sayisal_kolonlar = df.select_dtypes(include="number").columns
        eksik_sayisal = [col for col in sayisal_kolonlar if df[col].isnull().any()]
        secilen_kolon = st.multiselect("Sadece seçili kolonları doldurmak için seçin", eksik_sayisal)

        if "temp_tab2" not in st.session_state:
            st.session_state["temp_tab2"] = df.copy()
            st.session_state["undo_tab2"] = []

        # --- Sadece mevcut sayısal sütunlarla çalış ---
        valid_cols = [col for col in secilen_kolon if col in st.session_state["temp_tab2"].columns]

        disable_btn = False
        if valid_cols:
            has_missing = any(st.session_state["temp_tab2"][col].isnull().any() for col in valid_cols)
            if not has_missing:
                disable_btn = True
                st.warning("Seçilen kolonlarda eksik veri yok, doldurma işlemi yapılamaz.")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Doldur", key="btn_fill_tab2", disabled=disable_btn):
                st.session_state["undo_tab2"].append(st.session_state["temp_tab2"].copy())
                df_filled = st.session_state["temp_tab2"].copy()

                if doldurma_yontemi in ["ffill", "bfill"]:
                    df_filled[valid_cols] = df_filled[valid_cols].fillna(method=doldurma_yontemi)
                elif doldurma_yontemi == "Ortalama":
                    for col in valid_cols:
                        df_filled[col].fillna(df_filled[col].mean(), inplace=True)
                elif doldurma_yontemi == "Medyan":
                    for col in valid_cols:
                        df_filled[col].fillna(df_filled[col].median(), inplace=True)
                elif doldurma_yontemi == "Mod":
                    for col in valid_cols:
                        df_filled[col].fillna(df_filled[col].mode()[0], inplace=True)
                elif doldurma_yontemi == "Sabit Değer":
                    sabit_deger = st.text_input("Sabit değer girin", key="txt_sabit_tab2")
                    df_filled[valid_cols] = df_filled[valid_cols].fillna(sabit_deger)
                elif doldurma_yontemi == "Yapay Zeka (KNNImputer)":
                    imputer = KNNImputer(n_neighbors=3)
                    df_filled[valid_cols] = imputer.fit_transform(df_filled[valid_cols])

                st.session_state["temp_tab2"] = df_filled
                st.success("Eksik veriler dolduruldu ✅")
                st.dataframe(df_filled)

        with col2:
            if st.button("Geri Al", key="btn_undo_tab2") and st.session_state.get("undo_tab2_stack", []):
                st.session_state["temp_tab2"] = st.session_state["undo_tab2_stack"].pop()
                st.success("Son işlem geri alındı ✅")
                st.dataframe(st.session_state["temp_tab2"])

        with col3:
            if st.button("Ana DF'ye Kaydet", key="save_tab2"):
                st.session_state["data"] = st.session_state["temp_tab2"]
                st.success("Tab 2’deki değişiklikler ana DF’ye kaydedildi ✅")
