# Used in Spring 2019 to determine whether a file on disk was missing from a spreadsheet.

import csv
import os


def am_i_a_pid(variable: str) -> bool:
    if variable.startswith('utk'):
        return True
    else:
        return False


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


if __name__ == "__main__":
    theses_pids = get_pids_from_csv('/home/mark/PycharmProjects/trace_migrater/theses.csv')
    dissertations_pids = get_pids_from_csv('/home/mark/PycharmProjects/trace_migrater/dissertations.csv')

    for filename in os.walk('/home/mark/PycharmProjects/trace_migrater/my_files'):
        missing = []
        for file in filename[2]:
            new_name = file.replace('.xml', '').replace('_', ":")
            if new_name not in theses_pids and new_name not in dissertations_pids:
                missing.append(new_name)
        print(missing)
