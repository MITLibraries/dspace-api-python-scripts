import csv
import datetime
import glob
import os
import time

import structlog


logger = structlog.get_logger()


def create_csv_from_list(list_name, output):
    """Creates CSV file from list content."""
    with open(f'{output}.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id'])
        for item in list_name:
            writer.writerow([item])


def create_file_dict(file_path, file_type):
    """Creates a dict of file IDs and file paths."""
    files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
    file_dict = {}
    for file in files:
        file_name = os.path.splitext(os.path.basename(file))[0]
        file_dict[file_name] = file
    return file_dict


def create_ingest_report(items, file_name):
    """Creates ingest report of other systems' identifiers with a newly created
     DSpace handle."""
    with open(f'{file_name}', 'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(['uri'] + ['link'])
        for item in items:
            writer.writerow([item.source_system_identifier]
                            + [f'https://hdl.handle.net/{item.handle}'])


def create_metadata_id_list(metadata_csv):
    """Creates a list of IDs from a metadata CSV"""
    metadata_ids = []
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in [r for r in reader if r['file_identifier'] != '']:
            metadata_ids.append(row['file_identifier'])
    return metadata_ids


def elapsed_time(start_time, label):
    """Calculate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - start_time)
    logger.info(f'{label} : {td}')


def match_files_to_metadata(file_dict, metadata_ids):
    """Creates a list of files matched to metadata records."""
    file_matches = []
    for file_id, v in file_dict.items():
        for metadata_id in [m for m in metadata_ids
                            if file_id.startswith(m)]:
            file_matches.append(file_id)
    return file_matches


def match_metadata_to_files(file_dict, metadata_ids):
    """Creates a list of metadata records matched to files."""
    metadata_matches = []
    for metadata_id in metadata_ids:
        for file_id in [f for f in file_dict
                        if f.startswith(metadata_id)]:
            metadata_matches.append(metadata_id)
    return metadata_matches


def update_metadata_csv(metadata_csv, output_path, metadata_matches):
    """Creates an updated CSV of metadata records with matching files."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        upd_md_file_name = f'updated-{os.path.basename(metadata_csv)}'
        with open(f'{output_path}{upd_md_file_name}', 'w') as updated_csv:
            writer = csv.DictWriter(updated_csv, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row['file_identifier'] in metadata_matches:
                    writer.writerow(row)
