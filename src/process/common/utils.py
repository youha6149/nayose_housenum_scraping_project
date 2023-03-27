import os
import re
import unicodedata

import pandas as pd
from pandas import DataFrame

if __name__ == "__main__":
    from src.process.common.shaping import Shaping
else:
    from process.common.shaping import Shaping


class Util:
    def __init__(self) -> None:
        self.selection_cols = {
            "suumo": ["物件名", "住所", "最寄駅", "種別", "築年月", "構造", "階建", "総戸数"],
            "homes": ["物件名", "所在地", "交通", "物件種別", "築年月（築年数）", "建物構造", "建物階建", "総戸数"],
            "homemate": ["物件名", "所在地", "アクセス", "物件種別", "築年数", "建築構造", "居室階数", "総戸数"],
        }
        self.common_cols = [
            "name",
            "address",
            "access",
            "type",
            "yearpassed",
            "structure",
            "level",
            "housenum",
        ]

    def trans_cols_name(
        self, scrape_data_dict: dict[str, list[dict[str, int | str]]]
    ) -> DataFrame:
        """
        各スクレイピング処理から出力されたデータを各媒体ごとに必要なデータのみに絞り込んでいく

        args:
        data_dict: dict[str | list[dict]]
        ex -> {"suumo": [{"物件名": "ライオンズマンション", "総戸数": 30,,,}]}

        """

        site_name, scrape_data = list(scrape_data_dict.items())[0]
        # homesの場合、データの整備を行う
        if site_name == "homes":
            scrape_data_dict = self.trans_homes_data(scrape_data_dict)
            site_name, scrape_data = list(scrape_data_dict.items())[0]

        df = pd.DataFrame(scrape_data)

        cols = self.selection_cols[site_name]
        rename_dict = dict(zip(cols, self.common_cols))

        # 必要な列のみに選抜
        df = df[cols]
        df = df.rename(columns=rename_dict)
        # サイト名の列を追加
        df["site_name"] = [site_name for _ in range(len(df))]

        return df

    def trans_homes_data(self, scrape_data_dict: dict[str, list[dict[str, int | str]]]):
        site_name, data = list(scrape_data_dict.items())[0]
        correct_cols = self.selection_cols[site_name]

        # dataをループしてその要素の辞書にあってほしい列名がなければ追加する
        for d in data:
            for c in correct_cols:
                if c in d.keys():
                    continue
                d.update({c: None})

        return {site_name: data}

    def data_shaping(self, df: DataFrame) -> DataFrame:
        shaping = Shaping()
        df = shaping.homemate_address_shaping(df)
        df = shaping.suumo_access_shaping(df)
        df = shaping.yearpassed_shaping(df)
        df = shaping.homemate_level_normalize(df)
        df = shaping.homemate_level_shaping(df)
        df = shaping.homes_level_shaping(df)
        df = shaping.housenum_shaping(df)
        df = shaping.level_int_only(df)
        df = shaping.order_columns(df)
        return df
