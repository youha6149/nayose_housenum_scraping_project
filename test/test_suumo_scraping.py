import pdb
import traceback

from selenium.common.exceptions import NoSuchElementException

from log.logger import setup_logger
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.suumo.conditions import SuumoConditions
from process.suumo.scraper import SuumoScraper


def test_suumo_scraping():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()

    # 以下をまとめて関数として定義する
    with SuumoScraper() as bot:
        for i in range(len(housenum0_record)):
            try:
                print(i)
                record = housenum0_record[i]
                bot.scrape_suumo(record)

            except NoSuchElementException as e:
                print(e)
                print(traceback.format_exc())
                continue

            except Exception as e:
                print(e)
                print(traceback.format_exc())
                pdb.set_trace()

        pdb.set_trace()
        print(bot.row_data)


if __name__ == "__main__":
    test_suumo_scraping()
