import pdb

from log.logger import setup_logger
from process.suumo.conditions import SuumoConditions
from process.suumo.scraper import SuumoScraper


def test_suumo_scraping():
    property_names = ["アルス品川", "ライオンズマンション"]
    # 以下をまとめて関数として定義する
    with SuumoScraper() as bot:
        pdb.set_trace()
        for name in property_names:
            conditions = SuumoConditions(property_name=name, prefecture="東京都")
            if not conditions.time_walk == "":
                conditions.trans_raw_time_walk()
            try:
                bot.scrape_suumo(conditions=conditions)
            except Exception as e:
                logger = setup_logger("Scraper_logger", "scraper_error.log")
                logger.error(f"An error occurred: {e}")
                continue

        print(bot.row_data)


if __name__ == "__main__":
    test_suumo_scraping()
