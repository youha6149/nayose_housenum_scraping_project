import pdb
import time
import traceback

from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Scraper(webdriver.Chrome):
    def __init__(self, default_dl_path="", is_headless=False):
        self.driver_path = ChromeDriverManager().install()
        self.default_dl_path = default_dl_path
        options = webdriver.ChromeOptions()
        if is_headless:
            options.add_argument("--headless")
        if not self.default_dl_path == "":
            options.add_experimental_option(
                "prefs", {"download.default_directory": self.default_dl_path}
            )
        super(Scraper, self).__init__(executable_path=self.driver_path, options=options)
        self.implicitly_wait(15)
        self.set_script_timeout(5)
        self.waitng = WebDriverWait(self, 15)
        self.soup = ""

    def __exit__(self, exc_type, exc, traceback):
        self.quit()

    def page_is_loaded(self):
        is_loaded = self.execute_script("return document.readyState") == "complete"
        time.sleep(3)
        return is_loaded

    def open_page(self, url):
        self.get(url)
        self.waitng.until(lambda x: self.page_is_loaded())
        self.init_soup()

    def wait_presence_of_element_by_cssselector(self, selector: str, waittime: int):
        self.waitng.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        time.sleep(waittime)

    def init_soup(self):
        """ページ全体のBeautifulSoupを初期化する(DOM変化のたびに実行)"""
        self.soup = BeautifulSoup(self.page_source, "lxml")

    def init_src_element(self, src: Tag = "") -> Tag | BeautifulSoup:
        if not src == "":
            return src

        return self.soup

    def get_element_by_find(self, tag, src="", **attr) -> Tag | NavigableString:
        """.findを用いて要素取得を行う。要素がない場合NoSuchElementExceptionを返す"""
        src_elm = self.init_src_element(src)
        element = src_elm.find(tag, **attr)
        if element is None:
            raise NoSuchElementException(f"Element not found: {tag} {attr}")

        return element

    def get_elements_by_find_all(self, tag, src="", **attr) -> ResultSet:
        """.find_allを用いて複数の要素取得を行う。要素がない場合NoSuchElementExceptionを返す"""
        src_elm = self.init_src_element(src)
        elements = src_elm.find_all(tag, **attr)
        if elements is None:
            raise NoSuchElementException(f"Element not found: {tag} {attr}")

        return elements

    def get_element_by_select_one(self, selector, src="") -> Tag:
        """.select_oneを用いて要素取得を行う。要素がない場合NoSuchElementExceptionを返す"""
        src_elm = self.init_src_element(src)
        element = src_elm.select_one(selector)
        if element is None:
            raise NoSuchElementException(f"Element not found: {selector}")

        return element

    def get_elements_by_select(self, selector, src="") -> ResultSet[Tag]:
        """.selectを用いて複数の要素取得を行う。要素がない場合NoSuchElementExceptionを返す"""
        src_elm = self.init_src_element(src)
        elements = src_elm.select(selector)
        if elements is None:
            raise NoSuchElementException(f"Element not found: {selector}")

        return elements
