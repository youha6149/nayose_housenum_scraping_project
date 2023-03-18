import pdb
import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import (
    AbstractEventListener,
    EventFiringWebDriver,
)
from selenium.webdriver.support.ui import WebDriverWait

from process.common.scraper import Scraper


def test_webpage_check():
    with Scraper() as bot:
        pdb.set_trace()

        script = """
                    var observer = new MutationObserver(function(mutationsList) {
                        for(var mutation of mutationsList) {
                            if (mutation.type === 'childList') {
                                for(var node of mutation.addedNodes) {
                                    console.log(node);
                                }
                            }
                        }
                    });

                    observer.observe(document.body, { childList: true });
                """

        bot.open_page(
            "https://suumo.jp/library/search/ichiran.html?qr=%E3%82%AF%E3%83%AC%E3%83%BC%E3%83%AB%E8%A5%BF%E5%A4%A7%E5%AE%AE"
        )

        bot.execute_script(script)
        bot.waitng.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        bot.refresh()
        time.sleep(2)
        logs = bot.get_log("browser")
        for log in logs:
            if log["level"] == "INFO" and "console-api" in log["message"]:
                message = log["message"].split("console-api ")[-1]
                print(message)


if __name__ == "__main__":
    test_webpage_check()
