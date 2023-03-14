import os

import pandas as pd
from setting import Base, get_nayose_db, nayose_engine
from sqlalchemy import Column, Integer, String


class Nayose(Base):
    __tablename__ = "nayose"

    id = Column(Integer, primary_key=True)
    reid = Column(Integer)
    name = Column(String)
    address = Column(String)
    prefecture = Column(String)
    city = Column(String)
    town = Column(String)
    timewalk = Column(Integer)
    housenum = Column(Integer)


def insert_nayose_data():
    nayose_df = pd.read_csv(f"{os.getcwd()}/src/raw/nayose_raw - raw.csv")
    nayose_trans_df = nayose_df[
        [k for k in Nayose.__dict__.keys() if not k.startswith("_") and not k == "id"]
    ]
    nayose_trans_df.to_sql("nayose", nayose_engine)


if __name__ == "__main__":
    insert_nayose_data()
