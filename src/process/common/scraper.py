import json
import pdb
import time
import traceback

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from log.logger import setup_logger


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
        self.error_elements_exc: list[dict[str, str]] = []
        self.media_dict = {"media": type(self).__name__}

    def __exit__(self, exc_type, exc, traceback):
        if self.error_elements_exc:
            df = pd.DataFrame(self.error_elements_exc)
            df.to_csv("element_exc.csv")

        if exc:
            logger = setup_logger("Scraper_logger", "scraper_error.log")
            logger.error(f"An error occurred: {exc}")

        self.quit()

    def page_is_loaded(self):
        is_loaded = self.execute_script("return document.readyState") == "complete"
        time.sleep(2)
        return is_loaded

    def open_page(self, url):
        self.get(url)
        self.waitng.until(lambda x: self.page_is_loaded())

    def __add_element_error_detail(self, e: NoSuchElementException):
        tb = traceback.extract_tb(e.__traceback__)
        error_dict = {
            "media": type(self).__name__,
            **json.loads(e.msg),
            "file_name": tb[-1].filename,
            "error_location": tb[-1].lineno,
            "function_name": tb[-1].name,
        }
        self.error_elements_exc.append(error_dict)
