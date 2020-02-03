# Used in Spring 2019 to determine what thesis or dissertation was missing from dlshare.

import os
import csv


def get_pids_from_csv(a_csv: str) -> list:
    with open(a_csv, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='|')
        pids_from_string = []
        for row in csv_reader:
            parts = row['DELETE_original_uri_from_utk'].split('/')
            for part in parts:
                if part.startswith('utk'):
                    pids_from_string.append(part)
        return pids_from_string


def read_in_pdfs(a_path):
    for filename in os.walk(a_path):
        return [file.replace('.pdf', '').replace('_', ":") for file in filename[2]]


if __name__ == "__main__":
    theses = get_pids_from_csv('/home/mark/Documents/spring_2019/theses.csv')
    dissertations = get_pids_from_csv('/home/mark/Documents/spring_2019/dissertations.csv')
    pdfs = read_in_pdfs("/home/mark/PycharmProjects/trace_migrater/blah")
    embargoed_pdfs = read_in_pdfs("/home/mark/PycharmProjects/trace_migrater/embargos")

    for these in theses:
        if these not in embargoed_pdfs and these not in pdfs:
            print(these)

    for these in dissertations:
        if these not in embargoed_pdfs and these not in pdfs:
            print(these)
