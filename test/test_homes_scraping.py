import pdb

from log.logger import setup_logger
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.homes.conditions import HomesConditions
from process.homes.scraper import HomesScraper


def test_suumo_scraping():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()

    # 以下をまとめて関数として定義する
    with HomesScraper() as bot:
        for i in range(10):
            pdb.set_trace()
            record = housenum0_record[i]
            conditions = HomesConditions(
                name=record.name,
                prefecture=record.prefecture,
                city=record.city,
                town=record.town,
                time_walk=record.timewalk,
            )
            bot.scrape_homes(conditions=conditions)

        # for i in range(len(property_names)):
        # conditions = SuumoConditions(
        #     property_name=property_names[i],
        #     prefecture=prefectures[i],
        #     city=cities[i],
        # )
        # if not conditions.time_walk == "":
        #     conditions.trans_raw_time_walk()
        # try:
        #     bot.scrape_suumo(conditions=conditions)
        # except Exception as e:
        #     logger = setup_logger("Scraper_logger", "scraper_error.log")
        #     logger.error(f"An error occurred: {e}")
        #     continue

        print(bot.row_data)


if __name__ == "__main__":
    test_suumo_scraping()
