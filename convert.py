import os
import xmltodict
import csv
import json
import yaml
from app.email_handler import Person
from typing import Dict, Any
from app.embargo_handler import EmbargoedFiles, EmbargoHandler
from app.error_handler import ErrorLog
import requests
import tqdm
from app.pdf_handler import PdfManipulator
import arrow
import shutil


class FileSet:
    def __init__(self, path: str, embargoed_files=None, date_of_award: str="2017-12"):
        self.path = path
        self.files = self.build_set(path)
        self.embargos = embargoed_files
        self.date_of_award = date_of_award

    def __repr__(self):
        return f"A Fileset based on {self.path}."

    @staticmethod
    def build_set(path: str) -> list:
        for i in os.walk(path):
            return [file for file in i[2] if file.endswith(".xml")]

    @staticmethod
    def cleanup_processing_directory():
        for current_file in os.listdir(settings["processing_directory"]):
            file_path = os.path.join(settings["processing_directory"], current_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                error_log.write_error(f"WARNING: Exception occured on cleanup_processing_directory for {file_path} "
                                      f"as {e}.")

    def build_csv(self, metadata: list):
        headings = ["title", "DELETE_original_uri_from_utk", "fulltext_url", "keywords", "abstract", "author1_fname",
                    "author1_mname", "author1_lname", "author1_suffix", "author1_email", "author1_institution",
                    "advisor1", "advisor2", "advisor3", "author1_orcid", "disciplines", "comments", "degree_name",
                    "department", "document_type", "embargo_date", "instruct", "publication_date", "season"]
        with open("theses.csv", "w", encoding="utf-8") as theses_csv:
            dict_writer = csv.writer(theses_csv, delimiter="|")
            dict_writer.writerow(headings)
            for record in metadata:
                if record[19] == "thesis" and record[22] == self.date_of_award:
                    if self.embargos is not None:
                        record = self.find_relevant_embargo(record)
                    dict_writer.writerow(record)
        with open("dissertations.csv", "w") as dissertations_csv:
            dict_writer = csv.writer(dissertations_csv, delimiter="|")
            dict_writer.writerow(headings)
            for record in metadata:
                if record[19] == "dissertation" and record[22] == self.date_of_award:
                    if self.embargos is not None:
                        record = self.find_relevant_embargo(record)
                    dict_writer.writerow(record)
        return

    def process_records(self):
        print("Reviewing files and building spreadsheets: \n")
        self.build_csv([Record(record, self.path).prep_csv() for record in tqdm.tqdm(self.files)])
        print("\nDownloading PDFs for theses: \n")
        self.download_and_cleanup_pdfs("theses.csv")
        print("\nDownloading PDFs for dissertations: \n")
        self.download_and_cleanup_pdfs("dissertations.csv")
        print("\nDownloading embargoed theses.\n")
        self.download_embargoed_files("theses.csv")
        print("\nDownloading embargoed dissertations.\n")
        self.download_embargoed_files("dissertations.csv")
        print("\nCleaning up processing directory. \n")
        self.cleanup_processing_directory()
        print("\n Done.")
        return

    @staticmethod
    def download_and_cleanup_pdfs(filename):
        with open(filename, "r", encoding="utf-8") as pdf_sheet:
            lines = [line for line in pdf_sheet]
            for row in tqdm.tqdm(csv.reader(lines, delimiter="|"), total=len(lines)):
                if row[1].startswith("https:"):
                    r = requests.get(row[1])
                    if r.status_code == 200:
                        with open(f"{settings['processing_directory']}/{row[1].split('/')[-3]}.pdf", 'wb') as etds:
                            etds.write(r.content)
                            PdfManipulator(f"{settings['processing_directory']}/{row[1].split('/')[-3]}.pdf",
                                           settings['for_dlshare']).process_pdf()
        return

    @staticmethod
    def download_embargoed_files(filename):
        with open(filename, "r", encoding="utf-8") as pdf_sheet:
            lines = [line for line in pdf_sheet]
            for row in tqdm.tqdm(csv.reader(lines, delimiter="|"), total=len(lines)):
                if row[1].startswith("EMBARGOED OR DELETED: "):
                    current_file = EmbargoHandler(row[1].replace("EMBARGOED OR DELETED: ", ""))
                    current_file.download_pdf()
        return

    def find_relevant_embargo(self, my_row: list):
        my_file = f'{my_row[1].replace("https://trace.utk.edu/islandora/object/", "").replace("/datastream/PDF", "")}' \
                  f'.xml'
        for i in self.embargos:
            if my_file == i["filename"]:
                # print(i)
                my_row.pop(20)
                my_row.insert(20, i["embargo-until"])
                # my_row.append(i["datastreams"])
        return my_row


class Record:
    def __init__(self, our_record: str, our_path: str):
        self.metadata = self.read_metadata(our_record, our_path)
        self.path_on_server = ""
        self.url_path = self.set_url_path(our_record)

    @staticmethod
    def read_metadata(record: str, path: str) -> Dict[str, Any]:
        with open(f"{path}/{record}", 'r', encoding="utf-8") as my_file:
            x = my_file.read()
            return xmltodict.parse(x)

    def set_url_path(self, file: str) -> str:
        r = requests.get(f"https://trace.utk.edu/islandora/object/{file.replace('.xml', '/datastream/PDF').replace('_',':')}")
        if r.status_code == 200:
            self.path_on_server = f"{settings['path_on_dlshare']}/{file.replace('.xml', '.pdf').replace('_',':')}"
            return f"https://trace.utk.edu/islandora/object/{file.replace('.xml', '/datastream/PDF').replace('_',':')}"
        else:
            self.path_on_server = f"{settings['path_on_dlshare']}/embargoed_files/{file.replace('.xml', '.pdf').replace('_',':')}"
            return f"EMBARGOED OR DELETED: https://trace.utk.edu/islandora/object/" \
                   f"{file.replace('.xml', '/datastream/PDF').replace('_',':')}"

    def prep_csv(self) -> list:
        our_author = self.find_author_by_role()
        row = [self.find_title(), self.url_path, self.path_on_server, self.review_notes("Keywords Submitted by Author"),
               self.find_abstract(), our_author["name"]["first"], our_author["name"]["middle"],
               our_author["name"]["last"], our_author["name"]["suffix"],
               Person(our_author["name"]["first"], our_author["name"]["last"]).check_utk_email(),
               self.find_author_institution()]
        thesis_advisor = self.find_advisors("Thesis advisor")
        if type(thesis_advisor) is list:
            row.append(", ".join(str(x) for x in thesis_advisor))
        else:
            row.append("BAD DATA.  Check file!")
        advisors = self.find_advisors("Committee member")
        if type(advisors) is list:
            row.append(", ".join(str(x) for x in advisors))
        else:
            row.append("BAD DATA.  Check file!")
        row.append("")
        row.append(our_author["orcid"])
        row.append("")
        row.append(self.review_notes("Submitted Comment"))
        row.append(self.find_degree())
        row.append(self.find_discipline())
        row.append(self.is_thesis_or_dissertation())
        row.append("")
        row.append(self.find_publication_date())
        row.append("")
        row.insert(20, self.add_embargo_date(row[1], row[21]))
        return row

    def add_embargo_date(self, field_to_check_on, publication_date):
        if publication_date == settings['date_of_award'] and field_to_check_on.startswith("EMBARGOED OR DELETED: "):
            x = EmbargoHandler(field_to_check_on.replace("EMBARGOED OR DELETED: ", ""))
            return f'{arrow.get(x.get_embargo_until(), "YYYY-MM-DD")} 00:00'
        else:
            return ""

    def find_title(self) -> str:
        return self.metadata["mods:mods"]["mods:titleInfo"]["mods:title"]

    def find_abstract(self) -> str:
        if self.metadata["mods:mods"]["mods:abstract"]:
            return self.replace_returns(self.metadata["mods:mods"]["mods:abstract"])
        else:
            return ''

    @staticmethod
    def replace_returns(x: str) -> str:
        return "".join(x.splitlines())

    def find_author_institution(self) -> str:
        return self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:grantor"]

    def find_discipline(self) -> str:
        return self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:discipline"]

    def review_notes(self, display_label: str, default: str="") -> str:
        for note in self.metadata["mods:mods"]["mods:note"]:
            if note["@displayLabel"] == display_label:
                try:
                    default = note["#text"]
                except KeyError:
                    pass
        return default

    def find_degree(self) -> str:
        return self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:name"]

    def find_publication_date(self) -> str:
        return json.loads(json.dumps(self.metadata["mods:mods"]["mods:originInfo"]["mods:dateIssued"]["#text"]))

    def find_advisors(self, role: str) -> Any:
        matches = []
        for names in json.loads(json.dumps(self.metadata["mods:mods"]["mods:name"])):
            for k, v in names.items():
                if k == "mods:role":
                    try:
                        if v["mods:roleTerm"]["#text"] == role:
                            x = self.split_name_parts(names["mods:namePart"]).rstrip()
                            matches.append(x)
                    except KeyError:
                        error_log.write_error(f"Exception on find advisors: {self.url_path}")
                        return f"{self.url_path} has bad metadata and can't find advisors.'"
        return matches

    @staticmethod
    def split_name_parts(parts):
        full_name = {"suffix": ""}
        for part in parts:
            if part["@type"] == "given":
                full_name.update(first=part["#text"])
            elif part["@type"] == "family":
                full_name.update(last=part["#text"])
            elif part["@type"] == "termsOfAddress":
                try:
                    full_name.update(suffix=part["#text"])
                except KeyError:
                    full_name.update(suffix="")
        return f"{full_name['first']} {full_name['last']} {full_name['suffix']}"

    def find_author_by_role(self, role: str="Author") -> dict:
        author = {"name": "", "orcid": ""}
        for names in json.loads(json.dumps(self.metadata["mods:mods"]["mods:name"])):
            for k, v in names.items():
                if k == "mods:role":
                    try:
                        if v["mods:roleTerm"]["#text"] == role:
                            author.update(name=self.handle_author_parts(names["mods:namePart"]))
                            author.update(orcid=self.find_orcid(names))
                    except KeyError:
                        error_log.write_error(f"Exception on find author by role for {self.url_path}.")
        return author

    @staticmethod
    def handle_author_parts(parts: list) -> dict:
        full_name = {"suffix": "", "middle": ""}
        for part in parts:
            if part["@type"] == "given":
                split_given = part["#text"].split()
                full_name.update(first=split_given[0])
                if len(split_given) > 1:
                    full_name.update(middle=split_given[1])
            elif part["@type"] == "family":
                full_name.update(last=part["#text"])
            elif part["@type"] == "termsOfAddress":
                try:
                    full_name.update(suffix=part["#text"])
                except KeyError:
                    full_name.update(suffix="")
        return full_name

    @staticmethod
    def find_orcid(node) -> str:
        try:
            return node["@valueURI"]
        except KeyError:
            return ""

    def is_thesis_or_dissertation(self) -> str:
        if self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:level"] == 'Doctoral (includes ' \
                                                                                      'post-doctoral)':
            return "dissertation"
        else:
            return "thesis"


class ProcessRequest:
    def __init__(self, type="not_embargoed"):
        self.type = type

    def handle(self):
        if self.type == "not_embargoed":
            settings = yaml.load(open("config/config.yml", "r"))
            test = FileSet(settings["path"])
            test.process_records()
        elif self.type == "datastream":
            embargos = EmbargoedFiles("/home/mark/PycharmProjects/trace_unpublished/rels-int/", "datastream")
            embargos.build_mods()
            test = FileSet("test_mods", embargos.embargoed_files)
            print(test.embargos)
            test.process_records()
        elif self.type == "":
            embargos = EmbargoedFiles("/home/mark/PycharmProjects/trace_unpublished/rels-int/", "object")
            embargos.build_mods()
            test = FileSet("test_mods", embargos.embargoed_files)
            print(test.embargos)
            test.process_records()


settings = yaml.load(open("config/config.yml", "r"))
error_log = ErrorLog(settings["error_log"])

if __name__ == "__main__":
    test = FileSet(settings["path"], date_of_award="2018-08")
    test.process_records()
    # embargos = EmbargoedFiles("/home/mark/PycharmProjects/trace_unpublished/rels-int/", "datastream")
    # embargos.build_mods()
    # test = FileSet("test_mods", embargos.embargoed_files)
    # print(test.embargos)
    # test.process_records()
