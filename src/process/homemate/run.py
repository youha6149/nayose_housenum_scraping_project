import traceback

from selenium.common.exceptions import NoSuchElementException

from model.nayose import Nayose
from process.homemate.scraper import HomemateScraper

if __name__ == "__main__":
    from src.log.logger import setup_logger
else:
    from log.logger import setup_logger


def run(housenum0_record: list[Nayose]) -> list | None:
    logger = setup_logger("Scraper_logger", "scraper_error.log")
    with HomemateScraper() as bot:
        for record in housenum0_record:
            try:
                bot.scrape_homemate(record)

            except NoSuchElementException as e:
                logger.info(f"NoSuchElementException: {e}")
                logger.info(f"{traceback.format_exc()}")
                continue

            except Exception as e:
                logger.error(f"An error occurred: {e}")
                logger.error(f"{traceback.format_exc()}")
                return

        return bot.row_data


# Homemate
# ['賃料共益費', '敷金礼金', '敷引償却', '間取り', '居室階数', '専有面積', '方角', '築年数', '駐車場', '物件種別', '所在地', 'アクセス', 'キッチン', 'セキュリティー', '専用機能', '建物設備環境', '通信環境', '入居条件', 'バストイレ', '室内設備', '物件名', '物件No', '総戸数', '取引態様', '契約形態', 'その他費用', '家賃保証', '主な周辺施設'
