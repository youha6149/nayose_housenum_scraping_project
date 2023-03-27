import os
import re
import unicodedata

import pandas as pd


def test_data_shaping():
    df = pd.read_csv(f"{os.getcwd()}/test/csv/test_scraping.csv")

    df = df.drop("Unnamed: 0", axis=1)
    df["id"] = [i for i in range(1, len(df) + 1)]

    # homemate address shaping
    address_join = lambda x: " ".join([e for e in x.split(" ") if not e == ""])
    df_homemte_address = df.loc[df["site_name"] == "homemate", "address"]
    df.loc[df["site_name"] == "homemate", "address"] = df_homemte_address.apply(
        address_join
    )

    # homes access shaping
    access_join = lambda x: " ".join(
        [e for e in x.replace("\n", "").split("\t") if not e == ""]
    )
    df_suumo_access = df.loc[df["site_name"] == "suumo", "access"]
    df.loc[df["site_name"] == "suumo", "access"] = df_suumo_access.apply(access_join)

    # yearpassed shaping
    df["yearpassed"] = df["yearpassed"].str.extract(r"(\d{4}年\d{1,2}月)")
    df["yearpassed"] = pd.to_datetime(df["yearpassed"], format="%Y年%m月")

    # homemate level shaping full size to half size
    df_homemte_level = df.loc[df["site_name"] == "homemate", "level"]
    normalize = lambda x: unicodedata.normalize("NFKC", x)
    df.loc[df["site_name"] == "homemate", "level"] = df_homemte_level.apply(normalize)

    # homemate level shaping
    level_split = lambda x: x.split("/")[1]
    df_homemte_level = df.loc[df["site_name"] == "homemate", "level"]
    df.loc[df["site_name"] == "homemate", "level"] = df_homemte_level.apply(level_split)

    # homes level shaping
    level_split = lambda x: x.split("/")[0]
    df_homes_level = df.loc[df["site_name"] == "homes", "level"]
    df.loc[df["site_name"] == "homes", "level"] = df_homes_level.apply(level_split)

    # housenum shaping
    pattern = "\d{1,3}戸"
    re_find_all = lambda x: "".join(re.findall(pattern, x))
    df["housenum"] = df["housenum"].fillna("")
    df["housenum"] = df["housenum"].apply(re_find_all)
    df["housenum"] = df["housenum"].replace("", 0)

    # level int only
    num_only = lambda x: int(re.sub(r"[^0-9]+", "", x))
    df["level"] = df["level"].apply(num_only)

    # columns trans
    lst = [c for c in range(len(df.columns))]
    lst = lst[-1:] + lst[:-1]
    df = df.iloc[:, lst]

    df.to_csv(
        f"{os.getcwd()}/test/csv/scraping_shaping_data.csv",
        encoding="utf-8",
        index=False,
    )


if __name__ == "__main__":
    test_data_shaping()
