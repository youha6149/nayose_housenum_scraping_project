import glob
import io
import os
import zipfile
from datetime import date

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="housenum_scraping")

st.title("housenum_scraping")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if st.button("実行開始"):
    if uploaded_file is not None:
        files = {"file": uploaded_file.getvalue()}
        params = {"file_name": uploaded_file.name.split(".")[0]}
        headers = ({"accept": "application/json"},)
        response = requests.post(
            "http://localhost:8000/execute_scraping",
            params=params,
            files=files,
            headers=headers,
        )
        if response.ok:
            st.write("実行が完了しました。")
        else:
            st.error("送信に失敗しました。")
    else:
        st.warning("CSVファイルをアップロードしてください。")

if st.button("CSV取得"):
    csv_data_path = f"{os.getcwd()}/frontend/data"

    if os.path.exists(csv_data_path):
        for f in glob.glob(f"{csv_data_path}/*.csv"):
            os.remove(f)

    output_api_url = "http://0.0.0.0:8000/read_output_data"
    response = requests.get(output_api_url)
    if response.ok:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        zip_file.extractall(path=csv_data_path)

        for csv_file in glob.glob(f"{csv_data_path}/*.csv"):
            file_name = csv_file.split("/")[-1]
            with open(csv_file, "rb") as f:
                csv_data = f.read()
                st.download_button(
                    label=file_name,
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv",
                )
    else:
        st.error("CSV取得に失敗しました")
