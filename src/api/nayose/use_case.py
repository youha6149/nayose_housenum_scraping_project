import glob
import os
import shutil
from datetime import datetime

import pandas as pd
from fastapi import UploadFile
from pandas import DataFrame
from sqlalchemy.orm import Session

import process
from model.nayose import Nayose
from process.common.utils import Util


class NayoseScraperProcess:
    def __init__(self, file: UploadFile, file_name: str) -> None:
        self.upload_file_contents = file.file
        self.upload_file_name = file_name
        self.scraper_util = Util()
        self.db_dir_path = f"{os.getcwd()}/src/db"
        self.csv_dir_path = f"{os.getcwd()}/src/csv"
        self.csv_file_path = os.path.join(
            f"{self.csv_dir_path}/", self.upload_file_name
        )

    def __enter__(self):
        """処理に使うdb,csvファイルの作成"""
        with open(self.csv_file_path, "wb+") as upload_dir:
            shutil.copyfileobj(self.upload_file_contents, upload_dir)

        Nayose._init_data(self.csv_file_path)
        return self

    def __exit__(self, exc_type, exc, traceback):
        """処理に使ったdb,csvファイルの削除"""
        if os.path.exists(self.db_dir_path):
            for file_path in glob.glob(f"{self.db_dir_path}/*.db"):
                os.remove(file_path)

        if os.path.exists(self.csv_dir_path):
            for file_path in glob.glob(f"{self.csv_dir_path}/*.csv"):
                os.remove(file_path)

    def run_scraper(self, db: Session) -> list[DataFrame]:
        """各スクレイピング処理の実行"""
        merge_dfs_list = []
        nayose = Nayose()
        housenum0_record = nayose.read_nayose_data(db, housenum=0)
        for mod, func in process.run_mod_funcs:
            if "homes" in func:
                continue

            run_scraper = getattr(mod, func)
            scrape_data = run_scraper(
                housenum0_record=housenum0_record, is_headless=True
            )
            data = list(scrape_data.values())[0]

            if data and not scrape_data == None:
                df = self.scraper_util.trans_cols_name(scrape_data)
                merge_dfs_list.append(df)

        # for run_scraper in process.run_functions:
        #     scrape_data = run_scraper(housenum0_record)
        #     data = list(scrape_data.values())[0]
        #     if data and not scrape_data == None:
        #         df = self.scraper_util.trans_cols_name(scrape_data)
        #         merge_dfs_list.append(df)

        return merge_dfs_list

    def normalize_output_data(self, merge_dfs_list: list[DataFrame]) -> DataFrame:
        """出力されたデータを正規化する"""
        merge_df = pd.concat(merge_dfs_list, axis=0)
        merge_df["id"] = [i for i in range(1, len(merge_df) + 1)]
        normalize_merge_df = self.scraper_util.data_shaping(merge_df)
        return normalize_merge_df

    def create_csv(self, normalize_merge_df: DataFrame) -> str:
        """DFをCSVに変換して保存"""
        today = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{today}_{self.upload_file_name}_sh.csv"
        normalize_merge_csv_name = f"{os.getcwd()}/src/output/{file_name}"

        normalize_merge_df.to_csv(normalize_merge_csv_name, encoding="utf-8")
        return file_name
