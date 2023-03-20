import traceback

from selenium.common.exceptions import NoSuchElementException

from model.nayose import Nayose
from process.homemate.scraper import HomemateScraper
from src.log.logger import setup_logger


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
