import pdb
import traceback

import pandas as pd

from model.nayose import Nayose
from model.setting import get_nayose_db
from process.common.utils import Util
from process.homemate.run import run_homemate_scraper
from process.homes.run import run_homes_scraper
from process.suumo.run import run_suumo_scraper


# raw_dataを取得して、dbファイルに変換した前提で処理を行う
def test_data_trans_process():
    try:
        # nayoseのread処理を作成
        db = get_nayose_db()
        session = next(db)
        housenum0record = session.query(Nayose).filter_by(housenum=0).all()

        utils = Util()

        merge_dfs_list = []

        # TODO:run処理をまとめて実行する方法を探す
        # TODO:出力される実データの整形を行う
        # TODO:どのサイトからのデータなのかわかるようにしておく
        print("start suumo")
        suumo_output_data = run_suumo_scraper(housenum0record, is_headless=True)
        data = list(suumo_output_data.values())[0]
        if data and not suumo_output_data == None:
            suumo_df = utils.trans_cols_name(suumo_output_data)
            merge_dfs_list.append(suumo_df)

        print("start homemate")
        homemate_output_data = run_homemate_scraper(housenum0record, is_headless=True)
        data = list(homemate_output_data.values())[0]
        if data and not homemate_output_data == None:
            homemate_df = utils.trans_cols_name(homemate_output_data)
            merge_dfs_list.append(homemate_df)

        print("start homes")
        homes_output_data = run_homes_scraper(housenum0record, is_headless=False)
        data = list(homes_output_data.values())[0]
        if data and not homes_output_data == None:
            homes_df = utils.trans_cols_name(homes_output_data)
            merge_dfs_list.append(homes_df)

        merge_df = pd.concat(merge_dfs_list, axis=0)
        return merge_df

    except Exception as e:
        pdb.set_trace()
        print(e)
        print(traceback.format_exc())


if __name__ == "__main__":
    merge_df = test_data_trans_process()
    merge_df.to_csv("test_scraping.csv", encoding="utf-8")
