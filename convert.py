import os
import xmltodict
import csv


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

    def build_csv(self, metadata):
        headings = ["title", "abstract"]
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
        return row

    def find_title(self):
        return self.metadata["mods:mods"]["mods:titleInfo"]["mods:title"]

    def find_abstract(self):
        return self.metadata["mods:mods"]["mods:abstract"]

    def replace_returns(self):
        x = 0


if __name__ == "__main__":
    test = FileSet("/home/mark/metadata/utk_ir_td_fall_18/output")
    test.process_records()