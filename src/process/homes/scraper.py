from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from model.nayose import Nayose
from process.common.scraper import Scraper


class HomesScraper(Scraper):
    all_data_dict = {"homes": []}

    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://www.homes.co.jp"
        self.liblary_url = "https://www.homes.co.jp/archive/list/search/?keyword="

    def filtering_timewalk(self, timewalk: int):
        select_box = Select(self.find_element(By.ID, "cond_walkminutes"))

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

        if not timewalk == "":
            select_box.select_by_visible_text(timewalk)
        self.waitng.until(lambda x: self.page_is_loaded())
        self.init_soup()

    def get_links(self, record: Nayose) -> list | None:
        total_num_element = self.get_element_by_select_one("span.totalNum")
        # 次ページへ行くとブロックされるので絞り込みを行う(20=最大表示件数)
        if int(total_num_element.text) > 20:
            self.filtering_timewalk(record.timewalk)

            # DOMが変わるので再度total_num_elementを取得
            total_num_element = self.get_element_by_select_one("span.totalNum")
            if int(total_num_element.text) > 20:
                return

        # 所在地にnayoseデータの都道府県名+市区町村名が入っているもののみ取得
        property_lists = self.get_elements_by_select("div.mod-building.ui-frame-base")
        address = f"{record.prefecture}{record.city}"
        links = [
            self.get_element_by_select_one("h2 > a", l).get("href")
            for l in property_lists
            if address in self.get_element_by_select_one("p.address", l).text
        ]
        return links

    def scrape_table_data(self):

        specs = self.get_elements_by_select("table.mod-tableVertical")

        ths = [[th for th in self.get_elements_by_select("th", tbl)] for tbl in specs]
        ths = [[th.contents[0].strip() for th in th_l] for th_l in ths]
        # [['所在地', '交通'], ['物件種別', '築年月（築年数）', '建物構造', '建物階建', '総戸数'], ['設備・条件']]

        tds = [
            [td.text for td in self.get_elements_by_select("td", tbl)] for tbl in specs
        ]

        tds[0][0] = tds[0][0].split("\n")[1]
        tds[0][1] = ",".join([t for t in tds[0][1].split("\n") if not t == ""])
        tds = [[t.strip() for t in td] for td in tds]

        name = self.get_element_by_select_one("h1.heading.is-figure").text.strip()
        merge_dict = {"物件名": name}
        for d in [dict(zip(th, td)) for th, td in zip(ths, tds)]:
            merge_dict.update(d)

        self.all_data_dict["homes"].append(merge_dict)
