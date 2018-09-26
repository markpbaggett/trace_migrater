import os
import xmltodict
import csv
import json
import yaml
from app.email_handler import Person
from typing import Dict, Any


class FileSet:
    def __init__(self, path: str):
        self.path = path
        self.files = self.build_set(path)

    def __repr__(self):
        return f"A Fileset based on {self.path}."

    @staticmethod
    def build_set(path: str) -> list:
        for i in os.walk(path):
            return [file for file in i[2] if file.endswith(".xml")]

    @staticmethod
    def build_csv(metadata: list):
        headings = ["title", "fulltext_url", "keywords", "abstract", "author1_fname", "author1_mname", "author1_lname",
                    "author1_suffix", "author1_email", "author1_institution", "author1_orcid", "advisor1", "advisor2",
                    "disciplines", "comments", "degree_name", "document_type", "publication_date"]
        with open("final_csv.csv", "w") as trace_csv:
            dict_writer = csv.writer(trace_csv, delimiter="|")
            dict_writer.writerow(headings)
            for record in metadata:
                dict_writer.writerow(record)

    def process_records(self):
        return self.build_csv([Record(record, self.path).prep_csv() for record in self.files])


class Record:
    def __init__(self, our_record: str, our_path: str):
        self.metadata = self.read_metadata(our_record, our_path)
        self.url_path = self.set_url_path(our_record)

    @staticmethod
    def read_metadata(record: str, path: str) -> Dict[str, Any]:
        with open(f"{path}/{record}", 'r') as my_file:
            x = my_file.read()
            return xmltodict.parse(x)

    @staticmethod
    def set_url_path(file: str) -> str:
        return f"https://trace.utk.edu/islandora/object/{file.replace('.xml', '/datastream/PDF').replace('_',':')}"

    def prep_csv(self) -> list:
        our_author = self.find_author_by_role()
        row = [self.find_title(), self.url_path, self.review_notes("Keywords Submitted by Author"),
               self.find_abstract(), our_author["name"]["first"], our_author["name"]["middle"],
               our_author["name"]["last"], our_author["name"]["suffix"],
               Person(our_author["name"]["first"], our_author["name"]["last"]).check_utk_email(),
               self.find_author_institution(),
               our_author["orcid"]]
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
        row.append(self.find_discipline())
        row.append(self.review_notes("Submitted Comment"))
        row.append(self.find_degree())
        row.append(self.is_thesis_or_dissertation())
        row.append(self.find_publication_date())
        self.find_author_by_role()
        return row

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
                        print(self.url_path)
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
                        print(self.url_path)
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


if __name__ == "__main__":
    settings = yaml.load(open("config/config.yml", "r"))
    test = FileSet(settings["path"])
    test.process_records()
