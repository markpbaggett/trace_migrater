import os
import xmltodict
import json
import shutil
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome
import yaml
from app.pdf_handler import PdfManipulator
from app.error_handler import ErrorLog
from xml.parsers.expat import ExpatError


class EmbargoedFiles:
    def __init__(self, my_path: str, my_type: str="datastream"):
        self.type = my_type
        self.path = my_path
        self.files = self.populate(my_path)
        self.embargoed_files = self.get_embargo_dates()

    @staticmethod
    def populate(path: str) -> list:
        for i in os.walk(path):
            return [file for file in i[2] if file.endswith(".rdf+xml")]

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
                        print("key error")
                        error_log.write_error(f"A key error occured while getting the date associated with islandora-embargo:embargo-until for {self.path}{file}.")
                        pass
                else:
                    try:
                        files_with_dates.append({"filename": file, "embargo-until": data["rdf:RDF"]["rdf:Description"]["islandora-embargo:embargo-until"]["#text"], "datastreams": "all"})
                    except:
                        print("An unexpected error occurred.")
                        error_log.write_error(f"An unexpected error occurred while getting the embargo associated with {self.path}{file}.")
                        pass
        return files_with_dates

    @staticmethod
    def get_list_of_dsids(some_data: dict, a_filename: str) -> list:
        return [data['@rdf:about'].replace(f"info:fedora/{a_filename}/", '') for data in some_data]

    def build_mods(self, rels_int_files="rels201905/", path_to_mods="test_mods"):
        for file in self.embargoed_files:
            print(f"{self.path.replace(rels_int_files, 'my_files/')}{file['filename'].replace('rdf+xml', 'xml')}")
            shutil.copy(f"{self.path.replace(rels_int_files, 'my_files/')}{file['filename'].replace('rdf+xml', 'xml')}",
                        path_to_mods)


class EmbargoHandler:
    def __init__(self, identifier):
        self.identifier = identifier
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = Chrome(executable_path=os.path.abspath("/home/mark/bin/chromedriver"), options=self.options)

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
        try:
            r = self.driver.request("GET", self.identifier.replace("PDF", "RELS-INT"))
            data = json.loads(
                json.dumps(
                    xmltodict.parse(
                        r.content)
                )
            )
            return data["rdf:RDF"]["rdf:Description"][0]['islandora-embargo:embargo-until']["#text"][0:10]
        except ExpatError:
            error_log.write_error(f"ExpatError:  Could not get an embargo date for {self.identifier}.")
            return "9999-01-01"

    def download_pdf(self):
        self.setup_handler()
        self.driver.get(self.identifier)
        r = self.driver.request("GET", self.identifier)
        try:
            if r.status_code == 200:
                with open(f"{settings['for_dlshare']}/embargoed_files/{self.identifier.replace('https://trace.utk.edu/islandora/object/', '').replace('/datastream/PDF', '')}.pdf",
                        "wb") as my_file:
                    my_file.write(r.content)
                PdfManipulator(f"{settings['for_dlshare']}/embargoed_files/{self.identifier.replace('https://trace.utk.edu/islandora/object/', '').replace('/datastream/PDF', '')}.pdf", f"{settings['for_dlshare']}/embargoed_files").process_pdf()
            else:
                error_log.write_error(f"Downloading PDF with EmbargoHandler on {self.identifier} resulted in a "
                                      f"{r.status_code} error.")
            return
        except RuntimeError:
            error_log.write_error(f"RuntimeError: cannot join current thread on {self.identifier}.")
            return


settings = yaml.safe_load(open("config/config.yml", "r"))
error_log = ErrorLog(settings["error_log"])

if __name__ == "__main__":
    # test = EmbargoedFiles("/home/mark/PycharmProjects/trace_unpublished/rels-int/")
    # test.build_mods()
    test = EmbargoHandler("https://trace.utk.edu/islandora/object/utk.ir.td:131/datastream/PDF")
    test.get_embargo_until()
    test.download_pdf()
