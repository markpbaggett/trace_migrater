import os
import xmltodict
import csv
import json


class FileSet:
    def __init__(self, path):
        self.path = path
        self.files = self.build_set(path)

    def __repr__(self):
        return

    @staticmethod
    def build_set(path):
        for i in os.walk(path):
            return [file for file in i[2] if file.endswith(".xml")]

    @staticmethod
    def build_csv(metadata):
        headings = ["title", "abstract", "author1_fname", "author1_mname", "author1_lname", "author1_suffix",
                    "author1_institution"]
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

    @staticmethod
    def read_metadata(record, path):
        with open(f"{path}/{record}", 'r') as my_file:
            x = my_file.read()
            return xmltodict.parse(x)

    def prep_csv(self):
        row = []
        row.append(self.find_title())
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


if __name__ == "__main__":
    test = FileSet("/home/mark/metadata/utk_ir_td_fall_18/output")
    test.process_records()
