import pdb
import time
import traceback

from mod.measure_time_decorator import measure_time
from selenium.common.exceptions import NoSuchElementException

from log.logger import setup_logger
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.homes.scraper import HomesScraper


@measure_time
def test_suumo_scraping():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()
    for i in range(len(housenum0_record)):
        try:
            with HomesScraper() as bot:
                # 物件一覧ページに遷移
                print(i)
                bot.open_page(f"{bot.liblary_url}{housenum0_record[i].name}")
                time.sleep(1)
                # 物件一覧から各物件のURLを取得する
                links = bot.get_links(housenum0_record[i])

            if links is None:
                continue

            for link in links:
                with HomesScraper() as bot:
                    # 物件詳細ページに遷移
                    bot.open_page(f"{bot.base_url}{link}")
                    time.sleep(1)

                    bot.scrape_table_data()

                time.sleep(2)

        except NoSuchElementException as e:
            if "totalNum" == e.msg:
                continue
            print(e)
            print(traceback.format_exc())
            continue

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            pdb.set_trace()

    return HomesScraper.all_data


if __name__ == "__main__":
    test_suumo_scraping()
