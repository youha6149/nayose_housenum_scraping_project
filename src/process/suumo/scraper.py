import pdb

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from process.common.scraper import Scraper
from process.suumo.conditions import SuumoConditions


class SuumoScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://suumo.jp"
        self.liblary_url = "https://suumo.jp/library/search/ichiran.html?qr="
        self.row_data = []

    def get_table_links(self, selector):
        soup = BeautifulSoup(self.page_source, "lxml")
        links = [a["href"] for a in soup.select(selector=selector)]
        return links

    def filtering_condition(self, conditions: SuumoConditions):
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
        row_dict = {"物件名": soup.find("h1").text}

        trs = soup.select("#contents > div > div > div > table > tbody > tr")
        for tr in trs:
            # {"住所": "北海道 函館市 湯川町３"}
            th_texts = [th.text for th in tr.find_all("th")]
            td_texts = [td.text for td in tr.find_all("td")]
            zip_texts = zip(th_texts, td_texts)
            row_dict.update(dict(zip_texts))

        self.row_data.append(row_dict)

    def scrape_suumo(self, conditions: SuumoConditions):
        self.open_page(url=f"{self.liblary_url}{conditions.property_name}")
        self.filtering_condition(conditions)
        links = self.get_table_links("#contents > table > tbody > tr > td > div > a")

        for link in links:
            self.open_page(f"{self.liblary_url}{link}")
            self.scrape_contents()
