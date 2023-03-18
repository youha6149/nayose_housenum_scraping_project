import pdb
import re
import traceback

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from model.nayose import Nayose
from process.common.scraper import Scraper

# TODO:wait処理をcss_selectorとしてcommonクラスにまとめる


class HomemateScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://www.homemate.co.jp"
        self.liblary_url = "https://www.homemate.co.jp/keyword/"
        self.row_data = []

    def __get_table_links(self, record: Nayose):
        soup = BeautifulSoup(self.page_source, "lxml")

        tmp = soup.find("span", class_="m_prpty_result_head_hit").text
        total_num = int(re.sub(r"[^\d]+", "", tmp))

        if total_num == 0:
            return

        boxes = soup.find_all("section", class_="m_prpty_box")

        # 出力されたデータの件数が多い場合、地域の選択から絞り込みを行う
        if len(boxes) > 5:
            select_element = Select(self.find_element(By.ID, "list-city-select2"))
            pref = record.prefecture
            if pref not in [option.text for option in select_element.options]:
                return

            select_element.select_by_visible_text(pref)
            self.waitng.until(
                EC.presence_of_element_located((By.ID, "deqwas-collection"))
            )

            # 変化したHTMLを再度取得する
            soup = BeautifulSoup(self.page_source, "lxml")
            boxes = soup.find_all("section", class_="m_prpty_box")
            # 絞り込んでもデータ数が多い場合、ブランド名や地域名などのエラーデータの可能性あり
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

    def __scrape_contents(self, record: Nayose):
        soup = BeautifulSoup(self.page_source, "lxml")
        # 必要なデータは何か
        # 物件名・階数・物件種別・所在地・アクセス・構造
        data_element = [
            th.find_parent("table") for th in soup.select("table th.m_table_ws")
        ]
        property_dict = {
            re.sub(r"[^\w]+", "", d.find("th").text): re.sub(
                r"[^\w]+", "", d.find("td").text
            )
            for d in data_element
        }
        pdb.set_trace()
        self.row_data.append(property_dict)

    def scrape_homemate(self, record: Nayose):
        # 検索ボックスから検索
        self.open_page(f"{self.liblary_url}{record.name}/")
        self.waitng.until(EC.presence_of_element_located((By.ID, "deqwas-collection")))

        # 表示された情報を取得する
        links = self.__get_table_links(record)

        # 該当するデータが一つもない場合、returnする
        if not links:
            return "not links"
        pdb.set_trace()
        for link in links:
            self.open_page(url=f"{self.base_url}{link}")
            self.waitng.until(
                EC.presence_of_element_located((By.ID, "deqwas-collection"))
            )
            self.__scrape_contents(record)
