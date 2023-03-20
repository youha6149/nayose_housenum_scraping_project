from model.nayose import Nayose
from process.common.scraper import Scraper


class SuumoScraper(Scraper):
    def __init__(self, default_dl_path="", is_headless=False):
        super().__init__(default_dl_path, is_headless)
        self.base_url = "https://suumo.jp"
        self.liblary_url = "https://suumo.jp/library/search/ichiran.html?qr="
        self.row_data = []

    def get_links(self):
        result_boxes = self.get_elements_by_select(
            "#contents > table > tbody > tr > td > div > a"
        )
        links = [a["href"] for a in result_boxes]
        return links

    def scrape_contents(self):
        trs = self.get_elements_by_select(
            "#contents > div > div > div > table > tbody > tr"
        )
        row_dict = {"物件名": self.get_element_by_select_one("h1").text}
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

        links = self.get_links()
        # 該当するデータが一つもない場合、returnする
        if not links:
            return "not links"

        for link in links:
            self.open_page(url=f"{self.base_url}{link}")
            self.scrape_contents()
