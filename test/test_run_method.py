import os
import pdb
from datetime import datetime

import pandas as pd

import process
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.common.utils import Util


def test_run_method():
    """process.__init__で設定したスクレイピング実行モジュール群を呼び出してスクレイピングを実行するテスト"""
    db = get_nayose_db()
    session = next(db)
    housenum0record = session.query(Nayose).filter_by(housenum=0).all()
    utils = Util()
    merge_dfs_list = []
    pdb.set_trace()

    for run_scraper in process.run_functions:
        output_data = run_scraper(housenum0record)
        data = list(output_data.values())[0]
        if data and not output_data == None:
            df = utils.trans_cols_name(output_data)
            merge_dfs_list.append(df)

    merge_df = pd.concat(merge_dfs_list, axis=0)
    today = datetime.now().strftime("%Y%m%d%H%M%S")
    normalize_merge_csv_name = f"{os.getcwd()}/src/output/{today}_sh.csv"

    merge_df.to_csv(normalize_merge_csv_name, encoding="utf-8")


if __name__ == "__main__":
    test_run_method()
