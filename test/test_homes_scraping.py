import pdb
import time
import traceback

from selenium.common.exceptions import NoSuchElementException

from log.logger import setup_logger
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.homes.scraper import HomesScraper


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
            print(e)
            print(traceback.format_exc())
            continue

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            pdb.set_trace()

    pdb.set_trace()
    print(HomesScraper.all_data)
    # HOMES
    # ['所在地', '交通', '物件種別', '築年月（築年数）', '建物構造', '建物階建', '総戸数', '設備・条件']


if __name__ == "__main__":
    test_suumo_scraping()
