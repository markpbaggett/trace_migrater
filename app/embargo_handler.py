import os
import xmltodict
import json
import shutil


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
                try:
                    files_with_dates.append({"filename": file, "embargo-until": data["rdf:RDF"]["rdf:Description"][0]
                    ['islandora-embargo:embargo-until']["#text"], "datastreams": self.get_list_of_dsids(data["rdf:RDF"]["rdf:Description"],file.replace(".xml", ''))},)
                except KeyError:
                    pass
        return files_with_dates

    @staticmethod
    def get_list_of_dsids(some_data: dict, a_filename: str) -> list:
        return [data['@rdf:about'].replace(f"info:fedora/{a_filename}/", '') for data in some_data]

    def build_mods(self):
        for file in self.embargoed_files:
            shutil.copy(f"{self.path.replace('rels-int/', 'mods/')}{file['filename']}", "test_mods")


if __name__ == "__main__":
    test = EmbargoedFiles("/home/mark/PycharmProjects/trace_unpublished/rels-int/")
    test.build_mods()
