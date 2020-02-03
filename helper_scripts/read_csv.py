# Used in Spring 2019 migration to build text file for review and download.

import csv


def write_files_to_download(pid):
    with open('/home/mark/PycharmProjects/trace_migrater/embargoed_files_to_download.txt', 'a') as download_files:
        download_files.write(f'{pid}\n')


with open('/home/mark/PycharmProjects/trace_migrater/dissertations.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter='|')
    for row in csv_reader:
        if not row['embargo_date'].startswith('9999') and row['embargo_date'] != "":
            write_files_to_download(row['DELETE_original_uri_from_utk'].replace("EMBARGOED OR DELETED: ", "").replace(
                '/datastream/PDF', '').replace('https://trace.utk.edu/islandora/object/', '')
                                    )
