import datetime
import glob
import io
import os
import shutil
import traceback
import zipfile

import pandas as pd
from fastapi import APIRouter, Depends, FastAPI, File, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import process
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.common.utils import Util

router = APIRouter()


@router.get("/read_output_data")
def read_output_data():
    """スクレイピングによって作成されたCSVデータをZipに圧縮して出力する"""
    output_dir_path = f"{os.getcwd()}/src/output"
    if not os.path.exists(output_dir_path):
        return {"message": "not exists output data"}

    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, "w") as zf:
        for csv_file_path in glob.glob(f"{output_dir_path}/*.csv"):
            file_name = csv_file_path.split("/")[-1]
            zf.write(csv_file_path, arcname=file_name)

    response = Response(content=zip_data.getvalue(), media_type="application/zip")
    response.headers["Content-Disposition"] = 'attachment; filename="csv_files.zip"'

    return response


@router.post("/execute_scraping")
def execute_scraping(
    db: Session = Depends(get_nayose_db), file: UploadFile = File(...)
):
    try:
        # 1. rawファイルの取得
        name = f"test_{file.filename}"
        contents = file.file
        upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
        with open(upload_filepath, "wb+") as upload_dir:
            shutil.copyfileobj(contents, upload_dir)

        # 2. ファイルをdbに変換する
        Nayose._init_data(upload_filepath)

        # 3. 各スクレイピング処理の実行
        utils = Util()
        merge_dfs_list = []
        nayose = Nayose()
        housenum0_record = nayose.read_nayose_data(db, housenum=0)
        for run_scraper in process.run_functions:
            scrape_data = run_scraper(housenum0_record)
            data = list(scrape_data.values())[0]
            if data and not scrape_data == None:
                df = utils.trans_cols_name(scrape_data)
                merge_dfs_list.append(df)

        merge_df = pd.concat(merge_dfs_list, axis=0)
        merge_df["id"] = [i for i in range(1, len(merge_df) + 1)]
        # 4. 出力されたデータを正規化する
        normalize_merge_df = utils.data_shaping(merge_df)

        # 5. 使用したdbファイルを削除する
        db_dir_path = f"{os.getcwd()}/src/db"
        if os.path.exists(db_dir_path):
            for file_path in glob.glob(f"{db_dir_path}/*.db"):
                os.remove(file_path)

        # 6. 作成したDFをCSV化して返す
        today = datetime.date.today().strftime("%Y%m%d%H%M%S")
        normalize_merge_csv_name = f"{os.getcwd()}/src/output/{today}_sh.csv"

        normalize_merge_df.to_csv(normalize_merge_csv_name, encoding="utf-8")

        return {"message": "実行完了"}

    # エラー時に使用したCSVとdbファイルを削除するようにする
    except Exception as e:
        db_dir_path = f"{os.getcwd()}/src/db"
        if os.path.exists(db_dir_path):
            for file_path in glob.glob(f"{db_dir_path}/*.db"):
                os.remove(file_path)

        csv_dir_path = f"{os.getcwd()}/src/csv"
        if os.path.exists(csv_dir_path):
            for file_path in glob.glob(f"{csv_dir_path}/*.csv"):
                os.remove(file_path)

        print(traceback.format_exc())
        return e
