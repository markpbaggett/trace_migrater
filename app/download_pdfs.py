# Summer 2019 ETDs

import requests

admin = "admin"
password = "password"
filename = "dissertations.txt"


def download_file(path, pid):
    r = requests.get(f'http://localhost:8080/fedora/objects/{pid}/datastreams/PDF/content',
                     auth=(admin, password))
    with open(f'{path}/{pid}.pdf'.replace(':', '_'), 'wb') as download:
        download.write(r.content)


with open(filename, 'r') as etds:
    for line in etds:
        pid = line.split("https://trace.utk.edu/islandora/object/")[1].replace('/datastream/PDF', '').replace("\n", "")
        if line.startswith("EMBARGOED"):
            download_file("embargos", pid)
        else:
            download_file("", pid)
