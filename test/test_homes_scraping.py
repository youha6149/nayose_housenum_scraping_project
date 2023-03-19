import pdb
import time

from log.logger import setup_logger
from model.nayose import Nayose
from model.setting import get_nayose_db
from process.homes.scraper import HomesScraper


def test_suumo_scraping():
    db = get_nayose_db()
    session = next(db)
    housenum0_record = session.query(Nayose).filter_by(housenum=0).all()

    all_data = []
    for i in range(48, 58):
        try:
            with HomesScraper() as bot:
                # 物件一覧ページに遷移
                print(i)
                bot.open_page(f"{bot.liblary_url}{housenum0_record[i].name}")
                time.sleep(1)
                # 物件一覧から各物件のURLを取得する
                links = bot.get_table_links(housenum0_record[i])

            if links is None:
                continue

            for link in links:
                with HomesScraper() as bot:
                    # 物件詳細ページに遷移
                    bot.open_page(f"{bot.base_url}{link}")
                    time.sleep(1)

                    bot.scrape_table_data()
                    all_data.append(bot.row_data)

                time.sleep(2)

        except Exception as e:
            print(e)
            continue

    print(all_data)


if __name__ == "__main__":
    test_suumo_scraping()
