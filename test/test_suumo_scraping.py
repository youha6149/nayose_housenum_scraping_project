import pdb

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
        try:
            for i in range(10):
                print(i)
                record = housenum0_record[i]
                bot.scrape_suumo(record)

        except Exception as e:
            logger = setup_logger("Scraper_logger", "scraper_error.log")
            logger.error(f"An error occurred: {e}")
            pdb.set_trace()

        print(bot.row_data)


if __name__ == "__main__":
    test_suumo_scraping()
