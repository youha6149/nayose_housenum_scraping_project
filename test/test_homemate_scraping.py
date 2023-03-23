import pdb
import time
import traceback

from mod.measure_time_decorator import measure_time
from selenium.common.exceptions import NoSuchElementException

from model.nayose import Nayose
from model.setting import get_nayose_db
from process.homemate.scraper import HomemateScraper


@measure_time
def test_unit_homemate_read_nayose():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()

    with HomemateScraper() as bot:
        for i in range(len(housenum0_record)):
            try:
                print(i)
                record = housenum0_record[i]

                bot.scrape_homemate(record)

            except NoSuchElementException as e:
                if "totalNum" in e.msg:
                    continue

                print(e)
                print(traceback.format_exc())
                continue

            except Exception as e:
                print(e)
                print(traceback.format_exc())
                pdb.set_trace()

        return bot.row_data


if __name__ == "__main__":
    test_unit_homemate_read_nayose()
