import csv


def get_deleted_or_unpublished(csv_name: str) -> list:
    with open(csv_name) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        return [row['DELETE_original_uri_from_utk'].split("object/")[1].replace("/datastream/PDF", "") for row in reader if row['embargo_date'].startswith("9999")]


if __name__ == "__main__":
    not_published = get_deleted_or_unpublished("dissertations.csv")
    with open("check_these.txt", 'w') as check_em:
        for pid in not_published:
            check_em.write(f'{pid}\n')
