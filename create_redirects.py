import csv
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import tqdm
import os
import time

digital_commons_advance_search ="https://trace.tennessee.edu/do/search/advanced/?fq=virtual_ancestor_link:%22" \
                                "https://trace.tennessee.edu%22"


class MigratedETD:
    def __init__(self, title:str, islandora_path: str):
        self.islandora_path = islandora_path.replace("EMBARGOED OR DELETED: ", "")
        self.title = title
        self.options = Options()
        #self.options.add_argument("--headless")
        self.driver = Chrome(executable_path=os.path.abspath("/usr/bin/chromedriver"), options=self.options)

    def check_digital_commons(self):
        # Go to Advanced Search
        self.driver.get(digital_commons_advance_search)
        # Click the DropDown Box
        select_box = Select(self.driver.find_element_by_class_name("field-sel"))
        select_box.select_by_visible_text("Title")
        # input Title text and click submit
        search_field = self.driver.find_element_by_class_name("term")
        search_field.send_keys(self.title)
        self.driver.find_element_by_id("do-search-advanced").click()
        time.sleep(3)
        html_source = self.driver.page_source
        try:
            x = self.driver.find_element_by_xpath("//a[@class='pdf']").get_attribute("href")
            self.driver.close()
            return f"Redirect 301 {self.islandora_path.replace('https://trace.utk.edu/', '')} {x}\n"
        except NoSuchElementException:
            self.driver.close()
            return f"Could not find {self.islandora_path}\n"


class CSVReader:
    def __init__(self, path_to_csv):
        self.my_csv = path_to_csv
        self.redirects = []
        self.process_csv()

    def process_csv(self):
        with open(self.my_csv, "r", encoding="utf-8") as migrated_files_sheet:
            lines = [line for line in migrated_files_sheet]
            for row in tqdm.tqdm(csv.reader(lines, delimiter="|"), total=len(lines)):
                if row[0] != "title":
                    etd_to_process = MigratedETD(row[0], row[1]).check_digital_commons()
                    self.redirects.append(etd_to_process)
        RedirectWriter(self.redirects)
        print("\nDone.")
        return


class RedirectWriter:
    def __init__(self, redirects: list):
        self.redirect_file = "redirect.txt"
        self.redirects = redirects
        self.write_output()

    def write_output(self):
        with open(self.redirect_file, "w") as redirect_file:
            for redirect in self.redirects:
                redirect_file.write(redirect)
        return


if __name__ == "__main__":
    x = CSVReader("/home/mark/Documents/theses_nov7.csv")
