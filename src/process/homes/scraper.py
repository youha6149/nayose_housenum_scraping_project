import itertools
import pdb
import re
import time
import traceback

from bs4 import BeautifulSoup, NavigableString, Tag
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

    # TODO:total_num_element取得処理は共通処理に移動させる
    def get_total_num(self, tag, **attr) -> Tag | NavigableString | None:
        soup = BeautifulSoup(self.page_source, "lxml")
        total_num_element = soup.find(tag, **attr)
        soup.find(tag="span", class_="totalNum")
        return total_num_element

    def get_table_links(self, record: Nayose):
        attr = {"class_": "totalNum"}
        total_num_element = self.get_total_num("span", **attr)
        if total_num_element is None:
            return

        # 1物件に収まる物件数の最大値が20件
        # それを超えたら絞り込みを行う
        if int(total_num_element.text) > 20:
            select_box = Select(self.find_element(By.ID, "cond_walkminutes"))
            w_t = record.timewalk
            if type(w_t) == "str":
                return

            # 名寄せデータ上のtimewalkが正確かわからないため、
            # w_tの適切な徒歩分数範囲(例：timewalk=3なら"7分以内")より１ランク上のものを適用している
            if w_t <= 1:
                record.timewalk = "5分以内"
            elif w_t <= 5:
                record.timewalk = "7分以内"
            elif w_t <= 7:
                record.timewalk = "10分以内"
            elif w_t <= 10:
                record.timewalk = "15分以内"
            elif w_t <= 20:
                record.timewalk = "20分以内"
            else:
                record.timewalk = ""

            select_box.select_by_visible_text(record.timewalk)
            self.waitng.until(lambda x: self.page_is_loaded())

            # DOMが変わるので再度total_num_elementを取得
            total_num_element = total_num_element = self.get_total_num("span", **attr)
            # 絞り込んでもなお20件を超える場合、エラーデータの可能性あり
            if int(total_num_element.text) > 20:
                return

        # 所在地にnayoseデータの都道府県名+市区町村名が入っているもののみ取得
        soup = BeautifulSoup(self.page_source, "lxml")
        property_lists = soup.find_all("div", class_="mod-building ui-frame-base")
        address = f"{record.prefecture}{record.city}"
        links = [
            l.select_one("h2 > a").get("href")
            for l in property_lists
            if address in l.find("p", class_="address").text
        ]

        return links

    def scrape_table_data(self):
        soup = BeautifulSoup(self.page_source, "lxml")
        spec_tables = soup.find_all("table", class_="mod-tableVertical")

        ths = [
            [th.contents[0].strip() for th in tbl.find_all("th")] for tbl in spec_tables
        ]
        # [['所在地', '交通'], ['物件種別', '築年月（築年数）', '建物構造', '建物階建', '総戸数'], ['設備・条件']]

        tds = [[td.text for td in tbl.find_all("td")] for tbl in spec_tables]

        tds[0][0] = tds[0][0].split("\n")[1]
        tds[0][1] = ",".join([t for t in tds[0][1].split("\n") if not t == ""])
        tds = [[t.strip() for t in td] for td in tds]

        property_dict_in_list = [dict(zip(th, td)) for th, td in zip(ths, tds)]
        merge_dict = {}
        for d in property_dict_in_list:
            merge_dict.update(d)

        self.row_data.append(merge_dict)
