import os
import xmltodict
import csv
import json


class FileSet:
    def __init__(self, path):
        self.path = path
        self.files = self.build_set(path)

    def __repr__(self):
        return f"A Fileset based on {self.path}."

    @staticmethod
    def build_set(path):
        for i in os.walk(path):
            return [file for file in i[2] if file.endswith(".xml")]

    @staticmethod
    def build_csv(metadata):
        headings = ["title", "fulltext_url", "keywords", "abstract", "author1_fname", "author1_mname", "author1_lname",
                    "author1_suffix", "author1_institution", "advisor1", "advisor2", "disciplines", "comments",
                    "degree_name", "document_type", "publication_date"]
        with open("final_csv.csv", "w") as trace_csv:
            dict_writer = csv.writer(trace_csv, delimiter="|")
            dict_writer.writerow(headings)
            for record in metadata:
                dict_writer.writerow(record)

    def process_records(self):
        return self.build_csv([Record(record, self.path).prep_csv() for record in self.files])


class Record:
    def __init__(self, record, path):
        self.metadata = self.read_metadata(record, path)
        self.url_path = self.set_url_path(record)

    @staticmethod
    def read_metadata(record, path):
        with open(f"{path}/{record}", 'r') as my_file:
            x = my_file.read()
            return xmltodict.parse(x)

    @staticmethod
    def set_url_path(file):
        return f"https://trace.utk.edu/islandora/object/{file.replace('.xml', '/datastream/PDF').replace('_',':')}"

    def prep_csv(self):
        row = []
        row.append(self.find_title())
        row.append(self.url_path)
        row.append(self.review_notes("Keywords Submitted by Author"))
        row.append(self.find_abstract())
        given = self.find_author("given")
        if len(given) == 1:
            row.append(given[0])
            row.append("")
        else:
            row.append(given[0])
            row.append(given[1])
        row.append(self.find_author("family")[0])
        row.append(self.find_author("termsOfAddress")[0])
        row.append(self.find_author_institution())
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
        return row

    def find_title(self):
        return self.metadata["mods:mods"]["mods:titleInfo"]["mods:title"]

    def find_abstract(self):
        if self.metadata["mods:mods"]["mods:abstract"]:
            return self.replace_returns(self.metadata["mods:mods"]["mods:abstract"])
        else:
            return ''

    @staticmethod
    def replace_returns(x):
        return "".join(x.splitlines())

    def find_author(self, my_part):
        default = ""
        for names in json.loads(json.dumps(self.metadata["mods:mods"]["mods:name"])):
            for k, v in names.items():
                if k == "mods:namePart":
                    for part in v:
                        if part["@type"] == my_part:
                            try:
                                default = part["#text"]
                            except KeyError:
                                default = ""
        return default.split(" ")

    def find_author_institution(self):
        return self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:grantor"]

    def find_discipline(self):
        return self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:discipline"]

    def review_notes(self, display_label, default=""):
        for note in self.metadata["mods:mods"]["mods:note"]:
            if note["@displayLabel"] == display_label:
                try:
                    default = note["#text"]
                except KeyError:
                    pass
        return default

    def find_degree(self):
        return self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:name"]

    def find_publication_date(self):
        return json.loads(json.dumps(self.metadata["mods:mods"]["mods:originInfo"]["mods:dateIssued"]["#text"]))

    def find_advisors(self, role):
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

    def is_thesis_or_dissertation(self):
        if self.metadata["mods:mods"]["mods:extension"]["etd:degree"]["etd:level"] == 'Doctoral (includes ' \
                                                                                      'post-doctoral)':
            return "dissertation"
        else:
            return "thesis"


if __name__ == "__main__":
    test = FileSet("/home/mark/metadata/utk_ir_td_fall_18/output")
    test.process_records()
