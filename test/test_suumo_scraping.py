import pdb

from log.logger import setup_logger
from process.suumo.conditions import SuumoConditions
from process.suumo.scraper import SuumoScraper


def test_suumo_scraping():
    property_names = ["ジーメゾン西大宮", "ＤーＲＯＯＭ西大宮ＰＪ北棟", "エレガンテ"]
    prefectures = ["埼玉県", "埼玉県", "埼玉県"]
    cities = ["さいたま市西区", "さいたま市西区", "さいたま市西区"]

    # 以下をまとめて関数として定義する
    with SuumoScraper() as bot:
        pdb.set_trace()
        for i in range(len(property_names)):
            conditions = SuumoConditions(
                property_name=property_names[i],
                prefecture=prefectures[i],
                city=cities[i],
            )
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
