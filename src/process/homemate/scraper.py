import pdb
import re
import traceback

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from model.nayose import Nayose
from process.common.scraper import Scraper
from process.homemate.conditions import HomemateConditions


class HomemateScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://www.homemate.co.jp/"
        self.liblary_url = "https://www.homemate.co.jp/keyword/"
        self.row_data = []

    def __get_table_links(self, record: Nayose):
        soup = BeautifulSoup(self.page_source, "lxml")

        tmp = soup.find("span", class_="m_prpty_result_head_hit").text
        total_num = int(re.sub(r"[^\d]+", "", tmp))
        pdb.set_trace()

        if total_num == 0:
            return

        boxes = soup.find_all("section", class_="m_prpty_box")

        if len(boxes) > 5:
            select_element = Select(self.find_element(By.ID, "list-city-select2"))
            pref = record.prefecture
            if pref not in [option.text for option in select_element.options]:
                return
            boxes = soup.find_all("section", class_="m_prpty_box")

            if len(boxes) > 25:
                return

        search_address = f"{record.prefecture}{record.city}"
        links = [
            box.select_one(
                "div.m_prpty_itemlist_wrap > div.m_prpty_itemlist > div:nth-child(1) a.m_prpty_item_linkarea_btn.kpi_click"
            )["href"]
            for box in boxes
            if search_address in box.find("p", class_="m_prpty_maininfo_txt").text
        ]

        if links:
            return links

    def __scrape_contents(self):
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

    def scrape_homemate(self, record: Nayose):
        # 検索ボックスから検索
        pdb.set_trace()
        self.open_page(f"{self.liblary_url}{record.name}/")
        # wait処理をちゃんと実装した方がいいかもしれない
        # 表示された情報を取得する
        links = self.__get_table_links(record)

        # 該当するデータが一つもない場合、returnする
        if not links:
            return "not links"

        for link in links:
            self.open_page(url=f"{self.base_url}{link}")
            self.__scrape_contents()
