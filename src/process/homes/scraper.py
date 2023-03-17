import pdb
import time
import traceback

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from process.common.scraper import Scraper
from process.homes.conditions import HomesConditions


# MEMO:とりあえずキーワード検索から探す。
# 複数ページにまたがる場合、全てのページから住所等の情報が似ているものを抽出する
# 築年月は名寄せrawの対象データが更新された時期によって変化する可能性があるので、使えない
# 専有面積と間取りもデータが存在しない場合があるため、使うにしても工夫が必要
class HomesScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://www.homes.co.jp"
        self.liblary_url = "https://www.homes.co.jp/archive/list/search/?keyword="
        self.row_data = []

    def __get_table_links(self, conditions: HomesConditions):
        soup = BeautifulSoup(self.page_source, "lxml")
        pdb.set_trace()

        total_num = int(soup.find("span", {"class": "totalNum"}).text)
        if total_num > 20:
            select_box = Select(self.find_element(By.ID, "cond_walkminutes"))
            select_box.select_by_visible_text(conditions.time_walk)

        property_lists = soup.find_all("div", class_="mod-building ui-frame-base")
        address = f"{conditions.prefecture}{conditions.city}"

        links = [
            l.select_one("h2 > a").get("href")
            for l in property_lists
            if address in l.find("p", class_="address").text
        ]

        return links

    def scrape_table_data(self):
        soup = BeautifulSoup(self.page_source, "lxml")
        pdb.set_trace()
        div = soup.find("div", class_="p-bukkenDetailinfo")
        h2 = div.find("h2", class_="mod-headingText", text="物件概要")
        table = h2.find_next_sibling("table", class_="mod-tableVertical")

    def scrape_homes(self, conditions: HomesConditions):
        self.open_page(f"{self.liblary_url}{conditions.name}")
        # まず何件あるか確認する　→ 件数が20以上の場合、絞り込みを行う
        # → 基本的には徒歩分数
        # Homesの徒歩分数とデータ上の徒歩分数が違う場合どうするか？
        # それを見越してデータの徒歩分数範囲より一つ大きい範囲を設定に加えるか
        pdb.set_trace()
        conditions.trans_raw_time_walk()
        links = self.__get_table_links(conditions)

        for link in links:
            self.open_page(f"{self.base_url}{link}")
            time.sleep(3)
            self.scrape_table_data()
            # TODO:tableデータの取得処理を作成する
            # TODO:ブロックがかかってしまうので一旦終了
            # mod-tableVertical
