import itertools
import pdb
import re
import time
import traceback

from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from model.nayose import Nayose
from process.common.scraper import Scraper


class HomesScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://www.homes.co.jp"
        self.liblary_url = "https://www.homes.co.jp/archive/list/search/?keyword="
        self.row_data = []
        self.page_soup = ""

    # TODO:total_num_element取得処理は共通処理に移動させる
    # これをするなら、単一の要素取得は全てこれでいいのでは？
    def get_element_by_find(self, tag, **attr) -> Tag | NavigableString | None:
        """page_sourseから要素取得を行う。主にページ更新後の最初の要素取得で用いる"""
        soup = BeautifulSoup(self.page_source, "lxml")
        self.page_soup = soup
        element = soup.find(tag, **attr)
        return element

    def get_elements_by_find_all(self, tag, **attr) -> ResultSet:
        """page_sourseから複数の要素取得を行う。主にページ更新後の最初の要素取得で用いる"""
        soup = BeautifulSoup(self.page_source, "lxml")
        self.page_soup = soup
        elements = soup.find_all(tag, **attr)
        return elements

    def filtering_timewalk(self, timewalk: int):
        select_box = Select(self.find_element(By.ID, "cond_walkminutes"))

        # 名寄せデータ上のtimewalkが正確かわからないため、
        # timewalkの適切な徒歩分数範囲(例：timewalk=3なら"7分以内")より１ランク上のものを適用している
        if timewalk <= 1:
            timewalk = "5分以内"
        elif timewalk <= 5:
            timewalk = "7分以内"
        elif timewalk <= 7:
            timewalk = "10分以内"
        elif timewalk <= 10:
            timewalk = "15分以内"
        elif timewalk <= 20:
            timewalk = "20分以内"
        else:
            timewalk = ""

        select_box.select_by_visible_text(timewalk)
        self.waitng.until(lambda x: self.page_is_loaded())

    def get_table_links(self, record: Nayose) -> list | None:

        total_num_element = self.get_element_by_find("span", class_="totalNum")
        if total_num_element is None:
            return

        # 1物件に収まる物件数の最大値である20件を超えたら絞り込みを行う
        if int(total_num_element.text) > 20:
            # filteringメソッドとして定義する
            self.filtering_timewalk(record.timewalk)

            # DOMが変わるので再度total_num_elementを取得
            # 絞り込んでもなお20件を超える場合、エラーデータの可能性あり
            total_num_element = self.get_element_by_find("span", class_="totalNum")
            if int(total_num_element.text) > 20:
                return

        # 所在地にnayoseデータの都道府県名+市区町村名が入っているもののみ取得
        property_attr = {"class_": "mod-building ui-frame-base"}
        property_lists = self.get_elements_by_find_all("div", **property_attr)
        address = f"{record.prefecture}{record.city}"
        links = [
            l.select_one("h2 > a").get("href")
            for l in property_lists
            if address in l.find("p", class_="address").text
        ]

        return links

    def scrape_table_data(self):
        spec_tables = self.get_elements_by_find_all("table", class_="mod-tableVertical")
        ths = [
            [th.contents[0].strip() for th in tbl.find_all("th")] for tbl in spec_tables
        ]
        # [['所在地', '交通'], ['物件種別', '築年月（築年数）', '建物構造', '建物階建', '総戸数'], ['設備・条件']]

        tds = [[td.text for td in tbl.find_all("td")] for tbl in spec_tables]

        tds[0][0] = tds[0][0].split("\n")[1]
        tds[0][1] = ",".join([t for t in tds[0][1].split("\n") if not t == ""])
        tds = [[t.strip() for t in td] for td in tds]

        merge_dict = {}
        for d in [dict(zip(th, td)) for th, td in zip(ths, tds)]:
            merge_dict.update(d)

        self.row_data.append(merge_dict)
