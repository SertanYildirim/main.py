import streamlit as st
import pandas as pd
import sqlite3
import pymongo
from sqlalchemy import create_engine
import urllib
from urllib import parse

def run():
    st.subheader("📊 Data Export & Database Save")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"]

    export_type = st.selectbox(
        "Select Output Type",
        ["CSV", "Excel", "JSON", "Parquet", "SQLite (.db)", "PostgreSQL", "MSSQL", "MongoDB"]
    )

    file_name = st.text_input("File/Table/Collection Name", "output")

    # ------------------ FILE FORMATS ------------------
    if export_type == "CSV":
        if st.button("📥 Save as CSV"):
            file_path = f"{file_name}.csv"
            df.to_csv(file_path, index=False)
            st.success(f"✅ Data saved as {file_path}.")
            st.download_button("💾 Download", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "Excel":
        if st.button("📥 Save as Excel"):
            file_path = f"{file_name}.xlsx"
            df.to_excel(file_path, index=False)
            st.success(f"✅ Data saved as {file_path}.")
            st.download_button("💾 Download", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "JSON":
        if st.button("📥 Save as JSON"):
            file_path = f"{file_name}.json"
            df.to_json(file_path, orient="records", lines=True)
            st.success(f"✅ Data saved as {file_path}.")
            st.download_button("💾 Download", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "Parquet":
        if st.button("📥 Save as Parquet"):
            file_path = f"{file_name}.parquet"
            df.to_parquet(file_path)
            st.success(f"✅ Data saved as {file_path}.")
            st.download_button("💾 Download", open(file_path, "rb").read(), file_name=file_path)

    elif export_type == "SQLite (.db)":
        if st.button("📥 Save as SQLite Database (.db)"):
            file_path = f"{file_name}.db"
            conn = sqlite3.connect(file_path)
            df.to_sql(file_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success(f"✅ Data saved to SQLite database file ({file_path}).")
            st.download_button("💾 Download", open(file_path, "rb").read(), file_name=file_path)

    # ------------------ DATABASES ------------------
    elif export_type == "PostgreSQL":
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "5432")
        user = st.text_input("Username", "postgres")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database Name", "mydb")

        if st.button("📥 Export to PostgreSQL"):
            try:
                engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
                df.to_sql(file_name, engine, if_exists="replace", index=False)
                st.success(f"✅ Data exported to PostgreSQL table '{file_name}'.")
            except Exception as e:
                st.error(f"Error: {e}")

    elif export_type == "MSSQL":
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "1433")
        user = st.text_input("Username", "sa")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database Name", "mydb")

        if st.button("📥 Export to MSSQL"):
            try:
                params = urllib.parse.quote_plus(
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={host},{port};DATABASE={database};UID={user};PWD={password}"
                )
                engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
                df.to_sql(file_name, engine, if_exists="replace", index=False)
                st.success(f"✅ Data exported to MSSQL table '{file_name}'.")
            except Exception as e:
                st.error(f"Error: {e}")

    elif export_type == "MongoDB":
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "27017")
        user = st.text_input("Username (Optional)", "")
        password = st.text_input("Password (Optional)", type="password")
        database = st.text_input("Database Name", "mydb")

        if st.button("📥 Export to MongoDB"):
            try:
                if user and password:
                    uri = f"mongodb://{user}:{password}@{host}:{port}/{database}"
                else:
                    uri = f"mongodb://{host}:{port}/{database}"

                client = pymongo.MongoClient(uri)
                db = client[database]
                collection = db[file_name]

                collection.insert_many(df.to_dict("records"))
                st.success(f"✅ Data exported to MongoDB collection '{file_name}'.")
            except Exception as e:
                st.error(f"Error: {e}")
