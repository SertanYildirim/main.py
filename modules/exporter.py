import streamlit as st
import pandas as pd
import sqlite3
import pymongo
from sqlalchemy import create_engine
import urllib
from urllib import parse

def run():
    st.subheader("📊 Veri Dışa Aktarma & Veritabanı Kaydetme")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"]

    export_type = st.selectbox(
        "Çıktı Tipi Seçiniz",
        ["CSV", "Excel", "JSON", "Parquet", "SQLite (.db)", "PostgreSQL", "MSSQL", "MongoDB"]
    )

    file_name = st.text_input("Dosya/Tablo/Koleksiyon Adı", "output")

    # ------------------ DOSYA FORMATLARI ------------------
    if export_type == "CSV":
        if st.button("📥 CSV Olarak Kaydet"):
            file_path = f"{file_name}.csv"
            df.to_csv(file_path, index=False)
            st.success(f"✅ Veri {file_path} olarak kaydedildi.")
            st.download_button("💾 İndir", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "Excel":
        if st.button("📥 Excel Olarak Kaydet"):
            file_path = f"{file_name}.xlsx"
            df.to_excel(file_path, index=False)
            st.success(f"✅ Veri {file_path} olarak kaydedildi.")
            st.download_button("💾 İndir", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "JSON":
        if st.button("📥 JSON Olarak Kaydet"):
            file_path = f"{file_name}.json"
            df.to_json(file_path, orient="records", lines=True)
            st.success(f"✅ Veri {file_path} olarak kaydedildi.")
            st.download_button("💾 İndir", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "Parquet":
        if st.button("📥 Parquet Olarak Kaydet"):
            file_path = f"{file_name}.parquet"
            df.to_parquet(file_path)
            st.success(f"✅ Veri {file_path} olarak kaydedildi.")
            st.download_button("💾 İndir", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "SQLite (.db)":
        if st.button("📥 SQLite Veritabanı (.db) Olarak Kaydet"):
            file_path = f"{file_name}.db"
            conn = sqlite3.connect(file_path)
            df.to_sql(file_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Veri SQLite veritabanı dosyasına ({file_path}) kaydedildi.")
            st.download_button("💾 İndir", open(file_path, "rb").read(), file_name=file_path)

    # ------------------ VERİTABANLARI ------------------
    elif export_type == "PostgreSQL":
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "5432")
        user = st.text_input("Kullanıcı Adı", "postgres")
        password = st.text_input("Şifre", type="password")
        database = st.text_input("Veritabanı Adı", "mydb")

        if st.button("📥 PostgreSQL'e Aktar"):
            try:
                engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
                df.to_sql(file_name, engine, if_exists="replace", index=False)
                st.success(f"✅ Veri PostgreSQL veritabanına '{file_name}' tablosu olarak aktarıldı.")
            except Exception as e:
                st.error(f"Hata: {e}")

    elif export_type == "MSSQL":
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "1433")
        user = st.text_input("Kullanıcı Adı", "sa")
        password = st.text_input("Şifre", type="password")
        database = st.text_input("Veritabanı Adı", "mydb")

        if st.button("📥 MSSQL'e Aktar"):
            try:
                params = urllib.parse.quote_plus(
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={host},{port};DATABASE={database};UID={user};PWD={password}"
                )
                engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
                df.to_sql(file_name, engine, if_exists="replace", index=False)
                st.success(f"✅ Veri MSSQL veritabanına '{file_name}' tablosu olarak aktarıldı.")
            except Exception as e:
                st.error(f"Hata: {e}")

    elif export_type == "MongoDB":
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "27017")
        user = st.text_input("Kullanıcı Adı (opsiyonel)", "")
        password = st.text_input("Şifre (opsiyonel)", type="password")
        database = st.text_input("Veritabanı Adı", "mydb")

        if st.button("📥 MongoDB'ye Aktar"):
            try:
                if user and password:
                    uri = f"mongodb://{user}:{password}@{host}:{port}/{database}"
                else:
                    uri = f"mongodb://{host}:{port}/{database}"

                client = pymongo.MongoClient(uri)
                db = client[database]
                collection = db[file_name]

                collection.insert_many(df.to_dict("records"))
                st.success(f"✅ Veri MongoDB veritabanına '{file_name}' koleksiyonu olarak aktarıldı.")
            except Exception as e:
                st.error(f"Hata: {e}")
