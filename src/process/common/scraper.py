import pdb
import time
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
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

    def __exit__(self, exc_type, exc, traceback):
        self.quit()

    def page_is_loaded(self):
        is_loaded = self.execute_script("return document.readyState") == "complete"
        time.sleep(2)
        return is_loaded

    def open_page(self, url):
        self.get(url)
        self.waitng.until(lambda x: self.page_is_loaded())
