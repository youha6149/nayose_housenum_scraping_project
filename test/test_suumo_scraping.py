import pdb

from process.suumo.conditions import SuumoConditions
from process.suumo.scraper import SuumoScraper


def test_suumo_scraping():
    conditions = SuumoConditions(property_name="アルス品川", prefecture="東京都")
    with SuumoScraper() as bot:
        bot.scrape_suumo(conditions=conditions)
        print(bot.row_data)


if __name__ == "__main__":
    test_suumo_scraping()
