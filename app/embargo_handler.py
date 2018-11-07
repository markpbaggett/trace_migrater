import os
import xmltodict
import json
import shutil
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome
import yaml

settings = yaml.load(open("config/config.yml", "r"))

class EmbargoedFiles:
    def __init__(self, my_path: str, my_type: str="datastream"):
        self.type = my_type
        self.path = my_path
        self.files = self.populate(my_path)
        self.embargoed_files = self.get_embargo_dates()

    @staticmethod
    def populate(path: str) -> list:
        for i in os.walk(path):
            return [file for file in i[2] if file.endswith(".xml")]

    def get_embargo_dates(self) -> list:
        files_with_dates = []
        for file in self.files:
            with open(f"{self.path}{file}", 'r') as embargo:
                text = embargo.read()
                data = json.loads(json.dumps(xmltodict.parse(text)))
                if self.type == "datastream":
                    try:
                        files_with_dates.append({"filename": file, "embargo-until": data["rdf:RDF"]["rdf:Description"]
                        [0]['islandora-embargo:embargo-until']["#text"], "datastreams": self.get_list_of_dsids(data["rdf:RDF"]["rdf:Description"],file.replace(".xml", ''))},)
                    except KeyError:
                        pass
                else:
                    try:
                        files_with_dates.append({"filename": file, "embargo-until": data["rdf:RDF"]["rdf:Description"]["islandora-embargo:embargo-until"]["#text"], "datastreams": "all"})
                    except:
                        pass
        return files_with_dates

    @staticmethod
    def get_list_of_dsids(some_data: dict, a_filename: str) -> list:
        return [data['@rdf:about'].replace(f"info:fedora/{a_filename}/", '') for data in some_data]

    def build_mods(self):
        for file in self.embargoed_files:
            shutil.copy(f"{self.path.replace('rels-ext/', 'mods/')}{file['filename']}", "test_mods_rels_ext")


class EmbargoHandler:
    def __init__(self, identifier):
        self.identifier = identifier
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = Chrome(executable_path=os.path.abspath("/usr/bin/chromedriver"), options=self.options)
        self.setup_handler()

    def setup_handler(self):
        self.driver.get("https://trace.utk.edu/user/login")
        username = self.driver.find_element_by_id("username")
        password = self.driver.find_element_by_id("password")
        username.send_keys(settings["user_name"])
        password.send_keys(settings["password"])
        self.driver.find_element_by_name("submit").click()
        return

    def get_embargo_until(self):
        self.driver.get(self.identifier.replace("PDF", "RELS-INT"))
        r = self.driver.request("GET", self.identifier.replace("PDF", "RELS-INT"))
        data = json.loads(json.dumps(xmltodict.parse(r.content)))
        print(data["rdf:RDF"]["rdf:Description"][0]['islandora-embargo:embargo-until']["#text"])
        return

    def download_pdf(self):
        self.driver.get(self.identifier)
        r = self.driver.request("GET", self.identifier)
        if r.status_code == 200:
            with open(f"{settings['for_dlshare']}/embargoed_files/{self.identifier.replace('https://trace.utk.edu/islandora/object/', '').replace('/datastream/PDF', '')}.pdf",
                    "wb") as my_file:
                my_file.write(r.content)
        else:
            print(r.status_code)
            print(self.identifier)
        return


if __name__ == "__main__":
    # test = EmbargoedFiles("/home/mark/PycharmProjects/trace_unpublished/rels-int/")
    # test.build_mods()
    test = EmbargoHandler("https://trace.utk.edu/islandora/object/utk.ir.td:131/datastream/PDF")
    test.get_embargo_until()
    test.download_pdf()
