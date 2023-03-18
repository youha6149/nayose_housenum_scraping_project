from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from model.nayose import Nayose
from process.common.scraper import Scraper
from process.suumo.conditions import SuumoConditions


class SuumoScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://suumo.jp"
        self.liblary_url = "https://suumo.jp/library/search/ichiran.html?qr="
        self.row_data = []

    def __get_table_links(self):
        soup = BeautifulSoup(self.page_source, "lxml")
        links = [
            a["href"]
            for a in soup.select("#contents > table > tbody > tr > td > div > a")
        ]
        return links

    def __filtering_condition(self, conditions: SuumoConditions):
        self.find_element(By.CSS_SELECTOR, "a[title='条件を追加・変更する']").click()
        self.waitng.until(lambda x: self.page_is_loaded())

        xpath_str_dict = conditions.linked_element_dict()
        for k, v in conditions.to_dict().items():
            if k == "property_name" or k == "prefecture" or k == "city":
                continue
            if v:
                # 選択する値が誤っていてもそのまま処理を続ける
                try:
                    xpath_string = f"//li[contains(.//{xpath_str_dict[k]['tag']}, '{v}')]{xpath_str_dict[k]['to_input']}"
                    self.find_element(
                        By.XPATH,
                        xpath_string,
                    ).click()
                except NoSuchElementException as e:
                    self.__add_element_error_detail(e)
                    continue

        self.find_element(By.ID, "bottomSubmit").click()
        self.waitng.until(lambda x: self.page_is_loaded())

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

    def scrape_suumo(self, record: Nayose):
        self.open_page(
            url=f"{self.liblary_url}{record.name}+{record.prefecture}+{record.city}"
        )
        # MEMO:とりあえずキーワード検索でどの程度取得できるか確認してみて、精度が低かったら条件追加も行う方向性
        # self.__filtering_condition(conditions)

        links = self.__get_table_links()
        # 該当するデータが一つもない場合、returnする
        if not links:
            return "not links"

        for link in links:
            self.open_page(url=f"{self.base_url}{link}")
            self.__scrape_contents()
