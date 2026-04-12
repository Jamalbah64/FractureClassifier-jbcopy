from pathlib import Path
import csv
import os

rare_fractures = [
    '72B(b)',
    '72B(c)',
    '22-D/4.1',
    '23-E/2.1',
    '22u-D/1.1',
    '23r-E/7',
    '22u-D/4.1',
    '23u-E/3',
    '23r-E/3',
    '22r-D/5.1',
    '72B.(b)',
    '23u-E/1.1',
    '22r-D/1.1',
    '22-D/1.1',
    '23r-E/4.1',
    '23u-E7',
    '23r-E/4.2',
    '23r-E/2.2',
    '22r-D/1',
    '23u-E/4',
    '77.5.1A',
    '23u/E/7',
    '23r-M3.1',
    '23r-D/2.1',
    '22r-D/3.1',
    '77.1.1A',
    '77.4.1A',
    '77.3.1C',
    '77.2.1A',
    '76.2.A',
    '23-E/7',
    '23-E/1',
]

def get_matching_ids(col, should_remove):
    matching_ids = set()

    with open("./dataset.csv", "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=",")

        for row in reader:
            value = (row[col] or "").strip()
            image_id = (row["filestem"] or "").strip()

            if should_remove(value):
                matching_ids.add(image_id)

    return matching_ids

def delete_matching_files(matching_ids):
    deleted_count = 0

    for path in Path(".").iterdir():
        if not path.is_file():
            continue

        if path.stem in matching_ids:
            path.unlink()
            deleted_count += 1
            print("Deleted:", path.name)

    source_csv = "./dataset.csv"
    temp_csv = "./dataset.temp.csv"
    removed_row_count = 0

    with open(source_csv, "r", encoding="utf-8-sig", newline="") as infile, \
         open(temp_csv, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            image_id = (row["filestem"] or "").strip()

            if image_id in matching_ids:
                removed_row_count += 1
                continue

            writer.writerow(row)

    os.replace(temp_csv, source_csv)

    print("Deleted", deleted_count, "fractures from disk")
    print("Removed", removed_row_count, "fractures from csv")

    return deleted_count, removed_row_count
    
def remove_and_delete(reason, col, should_remove):
    print("----", reason, "----")
    fractures = get_matching_ids(col, should_remove)
    
    print(len(fractures), "removed for reason:", reason)
    delete_matching_files(fractures)
    
def main():
    remove_and_delete("multi-fractures", "ao_classification", lambda x: ";" in x)
    remove_and_delete("metal-fractures", "metal", lambda x: x == "1")
    remove_and_delete("projection-3", "projection", lambda x: x == "3")
    remove_and_delete("too-young", "age", lambda x: float(x) <= 2)
    remove_and_delete("too-rare", "ao_classification", lambda x: x in rare_fractures)

if __name__ == "__main__":
    main()
