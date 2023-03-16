import pdb

from model.nayose import Nayose
from model.setting import get_nayose_db
from process.suumo.conditions import SuumoConditions
from process.suumo.scraper import SuumoScraper


def test_read_nayose():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()
    print(housenum0_record[0].to_dict())


def test_unit_suumo_read_nayose():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()

    with SuumoScraper() as bot:
        for i in range(10):
            pdb.set_trace()
            record = housenum0_record[i]
            conditions = SuumoConditions(
                property_name=record.name,
                prefecture=record.prefecture,
                city=record.city,
                time_walk=record.timewalk,
            )
            bot.scrape_suumo(conditions=conditions)
        print(bot.row_data)


if __name__ == "__main__":
    test_unit_suumo_read_nayose()
