import re
import unicodedata

import pandas as pd
from pandas import DataFrame


class Shaping:
    def apply(
        self, df: DataFrame, func, for_idx: str, for_idx_val: str, for_col: str
    ) -> DataFrame:
        df_target_range = df.loc[df[for_idx] == for_idx_val, for_col]
        df.loc[df[for_idx] == for_idx_val, for_col] = df_target_range.apply(func)
        return df

    def homemate_address_shaping(self, df: DataFrame) -> DataFrame:
        setting = {
            "func": lambda x: " ".join([e for e in x.split(" ") if not e == ""]),
            "for_idx": "site_name",
            "for_idx_val": "homemate",
            "for_col": "address",
        }
        df = self.apply(df, **setting)
        return df

    def suumo_access_shaping(self, df: DataFrame) -> DataFrame:
        setting = {
            "func": lambda x: " ".join(
                [e for e in x.replace("\n", "").split("\t") if not e == ""]
            ),
            "for_idx": "site_name",
            "for_idx_val": "suumo",
            "for_col": "access",
        }
        df = self.apply(df, **setting)
        return df

    def yearpassed_shaping(self, df: DataFrame) -> DataFrame:
        df["yearpassed"] = df["yearpassed"].str.extract(r"(\d{4}年\d{1,2}月)")
        df["yearpassed"] = pd.to_datetime(df["yearpassed"], format="%Y年%m月")
        return df

    def homemate_level_normalize(self, df: DataFrame) -> DataFrame:
        setting = {
            "func": lambda x: unicodedata.normalize("NFKC", x),
            "for_idx": "site_name",
            "for_idx_val": "homemate",
            "for_col": "level",
        }
        df = self.apply(df, **setting)
        return df

    def homemate_level_shaping(self, df: DataFrame) -> DataFrame:
        setting = {
            "func": lambda x: x.split("/")[1],
            "for_idx": "site_name",
            "for_idx_val": "homemate",
            "for_col": "level",
        }
        df = self.apply(df, **setting)
        return df

    def homes_level_shaping(self, df: DataFrame) -> DataFrame:
        setting = {
            "func": lambda x: x.split("/")[0],
            "for_idx": "site_name",
            "for_idx_val": "homes",
            "for_col": "level",
        }
        df = self.apply(df, **setting)
        return df

    def housenum_shaping(self, df: DataFrame) -> DataFrame:
        re_find_all = lambda x: re.sub(
            r"[^0-9]+", "", "".join(re.findall("\d{1,3}戸", x))
        )
        df["housenum"] = df["housenum"].fillna("")
        df["housenum"] = df["housenum"].apply(re_find_all)
        df["housenum"] = df["housenum"].replace("", 0)
        return df

    def level_int_only(self, df: DataFrame) -> DataFrame:
        num_only = lambda x: int(re.sub(r"[^0-9]+", "", x))
        df["level"] = df["level"].apply(num_only)
        return df

    def order_columns(self, df: DataFrame) -> DataFrame:
        lst = [c for c in range(len(df.columns))]
        lst = lst[-1:] + lst[:-1]
        df = df.iloc[:, lst]
        return df
