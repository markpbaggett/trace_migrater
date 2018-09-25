from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import os

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=os.path.abspath("/usr/bin/chromedriver"), chrome_options=chrome_options)


class Person:
    def __init__(self, first: str, last: str):
        self.name = f"{first} {last}"

    def __repr__(self):
        return f"A person based on {self.name}."

    def check_utk_email(self) -> str:
        driver.get(f"https://directory.utk.edu/")
        text_box = driver.find_element_by_id("search-bar")
        text_box.send_keys(self.name)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        try:
            x = driver.find_element_by_xpath("//a[@class='ttinfo']")
            return x.text
        except NoSuchElementException:
            return ""
