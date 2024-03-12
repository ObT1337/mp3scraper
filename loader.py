import os
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MP3Downloader:
    def __init__(self):
        add_block_version = self.get_add_block_version()
        self.options = webdriver.ChromeOptions()
        # AddBlocker is now detected by the page
        # self.options.add_argument(
        #     "load-extension="
        #     + f"/Users/till/Library/Application Support/Google/Chrome/Default/Extensions/gighmmpiobklfepjocnamgkkbiglidom/{add_block_version}"
        # )
        # self.options.add_argument("--headless")
        self.web = webdriver.Chrome(options=self.options)
        self.loaded = "loaded.txt"
        self.missing = "missing.txt"
        self.consent = False

    def get_add_block_version(self):
        for dir in os.listdir(
            "/Users/till/Library/Application Support/Google/Chrome/Default/Extensions/gighmmpiobklfepjocnamgkkbiglidom/"
        ):
            if dir.startswith("."):
                continue
            return dir

    def wait_until_loaded(self, driver, find, selector=By.ID, timeout=2):
        try:
            myElem = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((selector, find))
            )
            print(f"Element with {selector} {find} is loaded")
            return True
        except TimeoutException:
            print(f"Waiting for element with {selector} {find} took too much time!")
            return False

    def load_results(self, track):
        web = self.web
        web.get("https://free-mp3-download.net/")

        if not self.consent:
            input("If you click consent, press a key!")
            self.consent = True

        query = web.find_element("id", "q")
        query.send_keys(track)
        search_button = web.find_element("id", "snd")
        web.execute_script("arguments[0].click();", search_button)

        if not self.wait_until_loaded(web, "q", timeout=5):
            return False
        res = web.find_element("id", "results")

        if not self.wait_until_loaded(res, "table", selector=By.XPATH, timeout=5):
            return False

        table = res.find_element(By.XPATH, "table")
        table = table.find_element(By.XPATH, "tbody")
        res = []
        for id, row in enumerate(table.find_elements(By.XPATH, "tr")):
            try:
                cols = row.find_elements(By.XPATH, "td")
                for col in cols:
                    print(col.text, end=", ")
                print("")
                name = cols[0].text
                duration = cols[2].text

                url = cols[3].find_element(By.XPATH, "a")
                button = url.find_element(By.XPATH, "button")
                res.append(
                    {
                        "name": name,
                        "duration": duration,
                        "url": url.get_attribute("href"),
                        "button": button,
                    }
                )
            except Exception as e:
                print()
                print(e)
                print(f"Result in row {id} could not be printed")
        return res

    def get_download_page(self, button):
        if not button:
            return False
        print(button)
        self.web.execute_script("arguments[0].click();", button)
        return True

    def quit(self):
        self.web.quit()

    def write_loaded(self, value):
        with open(self.loaded, "a+") as f:
            f.write(value)

    def write_missing(self, value):
        with open(self.missing, "a+") as f:
            f.write(value)


def main():
    mp3 = MP3Downloader()
    with open("tracks.txt", "r") as f:
        for line in f:
            res = mp3.load_results(line)
            if not res:
                mp3.write_missing(line)
                continue

            for idx, track in enumerate(res):
                print(idx, track["name"])
            while True:
                row = input("Which should be downloaded?")
                if row.isdigit():
                    break
                print("Please enter a number!")
            choice = res.pop(int(row))
            print(f"{choice} will be downloaded")

            if not mp3.get_download_page(choice["button"]):
                mp3.write_missing(line)
                continue

            input("Press enter to contiue")
            mp3.write_loaded(choice["name"] + "\n")


if __name__ == "__main__":
    main()
