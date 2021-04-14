import csv
import glob
import os


def create_csv_from_list(list_name, output):
    """Creates CSV file from list content."""
    with open(f'{output}.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id'])
        for item in list_name:
            writer.writerow([item])


def create_file_list(file_path, file_type):
    """Creates a list of file names."""
    files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
    file_list = [os.path.basename(file) for file in files]
    return file_list


def create_ingest_report(items, file_name):
    """Creates ingest report of other systems' identifiers with a newly created
     DSpace handle."""
    with open(f'{file_name}', 'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(['uri', 'link'])
        for item in items:
            writer.writerow([item.source_system_identifier]
                            + [f'https://hdl.handle.net/{item.handle}'])


def create_metadata_id_list(metadata_csv):
    """Creates a list of IDs from a metadata CSV"""
    metadata_ids = []
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        metadata_ids = [row['file_identifier'] for row in reader
                        if row['file_identifier'] != '']
    return metadata_ids


def match_files_to_metadata(file_list, metadata_ids):
    """Creates a list of files matched to metadata records."""
    file_matches = [file_id for metadata_id in metadata_ids
                    for file_id in file_list
                    if file_id.startswith(metadata_id)]
    return file_matches


def match_metadata_to_files(file_list, metadata_ids):
    """Creates a list of metadata records matched to files."""
    metadata_matches = [metadata_id for f in file_list for metadata_id in
                        metadata_ids if f.startswith(metadata_id)]
    return metadata_matches


def update_metadata_csv(metadata_csv, output_directory, metadata_matches):
    """Creates an updated CSV of metadata records with matching files."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        upd_md_file_name = f'updated-{os.path.basename(metadata_csv)}'
        with open(f'{output_directory}{upd_md_file_name}', 'w') as updated_csv:
            writer = csv.DictWriter(updated_csv, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row['file_identifier'] in metadata_matches:
                    writer.writerow(row)
