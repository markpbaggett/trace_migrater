# Used in Spring 2019 to build a CSV of bad files.

import csv


def copy_bad_files_to_csv(a_csv, a_new_csv_file):
    with open(a_csv, mode='r') as original_csv, open(a_new_csv_file, mode='w') as bad_files, open('list_of_bad_files.txt', 'a') as list_of_files:
        bad_file_count = 0
        headings = ["title", "DELETE_original_uri_from_utk", "fulltext_url", "keywords", "abstract", "author1_fname",
                    "author1_mname", "author1_lname", "author1_suffix", "author1_email", "author1_institution",
                    "advisor1", "advisor2", "advisor3", "author1_orcid", "disciplines", "comments", "degree_name",
                    "department", "document_type", "embargo_date", "instruct", "publication_date", "season"]
        writer = csv.DictWriter(bad_files, fieldnames=headings, delimiter='|')
        csv_reader = csv.DictReader(original_csv, delimiter='|')
        for row in csv_reader:
            if row['embargo_date'].startswith('9999'):
                writer.writerow(row)
                bad_file_count += 1
                list_of_files.write(row['DELETE_original_uri_from_utk'].replace("EMBARGOED OR DELETED: ", "").replace('/datastream/PDF', '\n').replace('https://trace.utk.edu/islandora/object/', ''))
        print(bad_file_count)


if __name__ == "__main__":
    copy_bad_files_to_csv('/home/mark/PycharmProjects/trace_migrater/theses.csv', '/home/mark/PycharmProjects/trace_migrater/bad_theses.csv')
    copy_bad_files_to_csv('/home/mark/PycharmProjects/trace_migrater/dissertations.csv', '/home/mark/PycharmProjects/trace_migrater/bad_dissertations.csv')
