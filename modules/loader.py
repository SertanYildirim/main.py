import streamlit as st
import pandas as pd
import io
import sqlite3
import os

# --- Loader fonksiyonların --- (senin verdiğin fonksiyonları kullanıyoruz)
def detect_delimiter(sample_text):
    delimiters = [",", ";", "\t", ":"]
    delimiter_counts = {d: sample_text.count(d) for d in delimiters}
    return max(delimiter_counts, key=delimiter_counts.get)

def parse_excel_with_delimiter(df):
    if df.shape[1] == 1:
        col_data = df.iloc[:, 0].astype(str)
        sample_text = "\n".join(col_data.head(5))
        delimiter = detect_delimiter(sample_text)
        df_split = col_data.str.split(delimiter, expand=True)
        df_split.columns = df_split.iloc[0]  # İlk satır kolon adı
        df_split = df_split[1:].reset_index(drop=True)
        return df_split
    return df

def detect_datetime_column(df, threshold=0.8, sample_size=100):
    for col in df.columns:
        try:
            sample = df[col].dropna().astype(str).head(sample_size)
            if len(sample) == 0:
                continue
            parsed = pd.to_datetime(sample, errors="coerce")
            ratio = parsed.notna().sum() / len(sample)
            if ratio >= threshold:
                return col
        except Exception:
            continue
    return None

def set_datetime_index(df):
    try:
        datetime_col = detect_datetime_column(df)
        if datetime_col:
            df = df.copy()
            df[datetime_col] = pd.to_datetime(df[datetime_col])
            df.set_index(datetime_col, inplace=True)
        return df
    except Exception as e:
        print(f"Datetime index ayarlama hatası: {e}")
        return df

def load_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1]
    match file_type:
        case "csv":
            sample = uploaded_file.read(1024).decode("utf-8")
            uploaded_file.seek(0)
            delimiter = detect_delimiter(sample)
            df = pd.read_csv(uploaded_file, delimiter=delimiter)
        case "xlsx":
            df_raw = pd.read_excel(uploaded_file, header=None)
            df = parse_excel_with_delimiter(df_raw)
        case "json":
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            df = pd.read_json(stringio)
        case "db":
            with open("temp_uploaded.db", "wb") as f:
                f.write(uploaded_file.read())
            conn = sqlite3.connect("temp_uploaded.db")
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
            if not tables.empty:
                table_name = tables['name'][0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
            else:
                conn.close()
                raise Exception("Veritabanında tablo bulunamadı.")
        case _:
            raise Exception("Desteklenmeyen dosya türü.")
    df = set_datetime_index(df)
    return df

# --- Streamlit arayüzü ---
def run():
    st.subheader("📂 Veri Yükleme")

    df = None

    # ------------------ Dosya Yükleme ------------------
    with st.expander("📁 Dışarıdan Dosya Yükle", expanded=True):
        uploaded_file = st.file_uploader("Veri dosyasını yükleyin", type=["csv", "xlsx", "json"])
        if uploaded_file is not None:
            try:
                df = load_file(uploaded_file)
                st.success("✅ Dosya başarıyla yüklendi.")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Dosya yüklenirken hata: {e}")

    # ------------------ Örnek Dataset ------------------
    with st.expander("📊 Örnek Veri Seti Kullan", expanded=True):
        datasets_path = "datasets"
        if not os.path.exists(datasets_path):
            st.error("⚠️ datasets klasörü bulunamadı.")
        else:
            dataset_files = [f for f in os.listdir(datasets_path) if f.endswith((".csv", ".xlsx", ".json"))]
            if dataset_files:
                selected_dataset = st.selectbox("Örnek veri setini seçin", dataset_files)
                if st.button("Örnek Veriyi Yükle"):
                    try:
                        file_path = os.path.join(datasets_path, selected_dataset)
                        with open(file_path, "rb") as f:
                            class UploadedFileMock:
                                def __init__(self, file):
                                    self.file = file
                                    self.name = selected_dataset
                                def read(self, n=-1):
                                    return self.file.read(n)
                                def seek(self, pos):
                                    self.file.seek(pos)
                                def getvalue(self):
                                    self.file.seek(0)
                                    return self.file.read()
                            uploaded_mock = UploadedFileMock(f)
                            df = load_file(uploaded_mock)
                        st.success(f"✅ {selected_dataset} başarıyla yüklendi.")
                        st.dataframe(df)
                    except Exception as e:
                        st.error(f"Hata: {e}")
            else:
                st.warning("datasets klasöründe veri bulunamadı.")

    # ------------------ Session State ------------------
    if df is not None:
        st.session_state["data"] = df
    elif "data" in st.session_state:
        st.info("Önceden yüklenmiş veri görüntüleniyor:")
        st.dataframe(st.session_state["data"])
    else:
        st.warning("Henüz veri yüklenmedi.")