import traceback

from selenium.common.exceptions import NoSuchElementException

from model.nayose import Nayose
from process.common.utils import Util
from process.homes.scraper import HomesScraper

if __name__ == "__main__":
    from src.log.logger import setup_logger
else:
    from log.logger import setup_logger


def run_homes_scraper(
    housenum0_record: list[Nayose], is_headless=False
) -> dict[str, list[dict[str, int | str]]] | None:
    util = Util()
    logger = setup_logger("Scraper_logger", "scraper_error.log")
    for record in housenum0_record:
        try:
            with HomesScraper(is_headless=is_headless) as bot:
                # 物件一覧ページに遷移
                bot.open_page(f"{bot.liblary_url}{record.name}")
                # 物件一覧から各物件のURLを取得する
                links = bot.get_links(record)

            if links is None:
                continue

            for link in links:
                with HomesScraper(is_headless=is_headless) as bot:
                    # 物件詳細ページに遷移
                    bot.open_page(f"{bot.base_url}{link}")
                    bot.scrape_table_data()

        except NoSuchElementException as e:
            if "totalNum" in e.msg:
                continue
            logger.info(f"NoSuchElementException: {e}")
            logger.info(f"{traceback.format_exc()}")
            continue

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(f"{traceback.format_exc()}")
            if HomesScraper.all_data:
                util.trans_cols_name(HomesScraper)
                return HomesScraper.all_data
            return

    if HomesScraper.all_data:
        util.trans_cols_name(HomesScraper.all_data)

    return {"homes": HomesScraper.all_data}
