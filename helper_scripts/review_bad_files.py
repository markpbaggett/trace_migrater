# Used in Spring 2019 for directory comparisons.

import os

bad_things = []
blah_files = []
embargoed_files = []
test_mods = []

for thing in os.walk('/home/mark/PycharmProjects/trace_migrater/blah'):
    for filename in thing[2]:
        blah_files.append(filename.replace('.pdf', ''))

for thing in os.walk('/home/mark/PycharmProjects/trace_migrater/embargos'):
    for filename in thing[2]:
        embargoed_files.append(filename.replace('.pdf', ''))

for thing in os.walk('/home/mark/PycharmProjects/trace_migrater/test_mods'):
    for filename in thing[2]:
        test_mods.append(filename.replace('.xml', ''))

for file in test_mods:
    if file.replace('_', ':') not in embargoed_files:
        print(file)
