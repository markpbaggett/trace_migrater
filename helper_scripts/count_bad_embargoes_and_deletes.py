# Used in Spring 2019 migration to determine the number of theses and dissertations that were deleted, unpublished, or
# had a bad embargo.

import csv

bad_files = 0
with open('/home/mark/PycharmProjects/trace_migrater/dissertations.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter='|')
    for row in csv_reader:
        if row['embargo_date'].startswith('9999'):
            bad_files += 1

with open('/home/mark/PycharmProjects/trace_migrater/theses.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter='|')
    for row in csv_reader:
        if row['embargo_date'].startswith('9999'):
            bad_files += 1

print(bad_files)