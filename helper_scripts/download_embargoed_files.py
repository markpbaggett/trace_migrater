# Used in Spring 2019 migration to download PDFs.

import requests

with open('embargoed_files_to_download.txt', 'r') as embargos:
    for line in embargos:
        pid = line.replace("\n", "")
        r = requests.get(f'http://localhost:8080/fedora/objects/{pid}/datastreams/PDF/content', auth=("username", "password"))
        with open(f'embargos/{pid}.pdf'.replace('?', ''), 'wb') as download:
            download.write(r.content)
