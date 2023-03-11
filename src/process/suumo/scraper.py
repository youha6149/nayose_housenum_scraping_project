import pdb

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from process.common.scraper import Scraper
from process.suumo.conditions import SuumoConditions


class SuumoScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.row_data = []

    def get_table_links(self, selector):
        soup = BeautifulSoup(self.page_source, "lxml")
        authors = soup.select(selector=selector)
        links = [a["href"] for a in authors]
        return links

    # 絞り込みを行う処理を作成する
    def filtering_condition(self, conditions: SuumoConditions):
        pdb.set_trace()
        self.find_element(By.CSS_SELECTOR, "a[title='条件を追加・変更する']").click()
        self.waitng.until(lambda x: self.page_is_loaded())

        xpath_str_dict = conditions.linked_element_dict()
        for k, v in conditions.to_dict().items():
            if v:
                xpath_string = f"//li[contains(.//{xpath_str_dict[k]['tag']}, '{v}')]{xpath_str_dict[k]['to_input']}"
                self.find_element(
                    By.XPATH,
                    xpath_string,
                ).click()

        self.find_element(By.ID, "bottomSubmit").click()
        self.waitng.until(lambda x: self.page_is_loaded())

    def scrape_contents(self):
        soup = BeautifulSoup(self.page_source, "lxml")
        row_dict = {"物件名", soup.find("h1")}

        trs = soup.select("#contents > div > div > div > table > tr")
        for tr in trs:
            # {"住所": "北海道 函館市 湯川町３"}
            row_dict.update(dict(zip(tr.find_all("th"), tr.find_all("td"))))

        self.row_data.append()
