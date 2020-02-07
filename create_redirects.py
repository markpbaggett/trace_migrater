import csv
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import tqdm
import os
import time
import uuid

digital_commons_advance_search = "https://trace.tennessee.edu/do/search/advanced/?fq=virtual_ancestor_link:%22" \
                                 "https://trace.tennessee.edu%22"


class MigratedETD:
    def __init__(self, title: str, islandora_path: str):
        self.islandora_path = islandora_path.replace("EMBARGOED OR DELETED: ", "")
        self.title = title
        self.options = Options()
        #self.options.add_argument("--headless")
        self.driver = Chrome(executable_path=os.path.abspath("/usr/bin/chromedriver"), options=self.options)

    def check_digital_commons(self) -> tuple:
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
            digital_commons_link = self.driver.find_element_by_xpath("//span[@class='title']/a").get_attribute("href")
            self.driver.close()
            return self.islandora_path.replace('https://trace.utk.edu', ''), digital_commons_link
        except NoSuchElementException:
            self.driver.close()
            return self.islandora_path.replace('https://trace.utk.edu', ''), 'Missing'


class CSVReader:
    def __init__(self, path_to_csv):
        self.my_csv = path_to_csv
        self.process_csv()

    def process_csv(self) -> int:
        redirects = []
        with open(self.my_csv, "r", encoding="utf-8") as migrated_files_sheet:
            lines = [line for line in migrated_files_sheet]
            for row in tqdm.tqdm(csv.reader(lines, delimiter="|"), total=len(lines)):
                if row[0] != "title":
                    etd_to_process = MigratedETD(row[0], row[1]).check_digital_commons()
                    redirects.append(etd_to_process)
        RedirectWriter(redirects, self.my_csv)
        print("\nDone.")
        return len(redirects)


class RedirectWriter:
    def __init__(self, redirects: list, file_name: str):
        self.redirect_file = file_name.replace('.csv', '_processed.csv')
        self.redirects = redirects
        self.write_output()

    def write_output(self):
        records_written = 0
        with open(self.redirect_file, mode='w') as redirect_file:
            headings = ['type', 'hash', 'source', 'source_options', 'redirect', 'redirect_options', 'status']
            writer = csv.DictWriter(
                redirect_file,
                delimiter='|',
                fieldnames=headings,
                quotechar="'"
            )
            writer.writeheader()
            for redirect in self.redirects:
                writer.writerow(
                    {
                        'type': 'redirect',
                        'hash': uuid.uuid4(),
                        'source': redirect[0],
                        'source_options': 'a:0:{}',
                        'redirect': redirect[1],
                        'redirect_options': 'a:1:{s:5:"https";b:1;}',
                        'status': '1'
                    }
                )
                records_written += 1
        return records_written


if __name__ == "__main__":
    x = CSVReader("/home/mark/PycharmProjects/trace_migrater/201905/test_theses.csv")
