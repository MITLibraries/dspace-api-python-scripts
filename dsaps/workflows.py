import csv
import glob
import os

from dsaps import models


def create_file_dict_and_list(file_path, file_type):
    """Creates a dict of file IDs and file paths and a list of file IDs."""
    if file_path.startswith('http'):
        file_dict = models.build_file_dict_remote(file_path, file_type, {})
    else:
        files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
        file_dict = {}
        file_ids = []
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_dict[file_name] = file
            file_ids.append(file_name)
    return file_dict, file_ids


def create_metadata_id_list(metadata_csv):
    """Creates a list of IDs from a metadata CSV"""
    metadata_ids = []
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = row['file_identifier']
            metadata_ids.append(value)
    return metadata_ids


def match_files_to_metadata(file_dict, file_ids, metadata_ids):
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
        for file_id in file_dict:
            if file_id.startswith(metadata_id):
                metadata_matches.append(metadata_id)
    return metadata_matches


def reconcile_files_and_metadata(metadata_csv, file_path, file_type):
    """Runs a reconciliation of files and metadata."""
    file_dict, file_ids = create_file_dict_and_list(file_path, file_type)
    metadata_ids = create_metadata_id_list(metadata_csv)
    metadata_matches = match_metadata_to_files(file_dict, metadata_ids)
    file_matches = match_files_to_metadata(file_dict, file_ids, metadata_ids)
    no_files = set(metadata_ids) - set(metadata_matches)
    no_metadata = set(file_ids) - set(file_matches)
    models.create_csv_from_list(no_metadata, 'no_metadata')
    models.create_csv_from_list(no_files, 'no_files')
    models.create_csv_from_list(metadata_matches, 'metadata_matches')
    update_metadata_csv(metadata_csv, metadata_matches)


def update_metadata_csv(metadata_csv, metadata_matches):
    """Creates an updated CSV of metadata records with matching files."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        upd_md_file_name = f'updated-{os.path.basename(metadata_csv)}'
        with open(f'{upd_md_file_name}', 'w') as updated_csv:
            writer = csv.DictWriter(updated_csv, fieldnames=reader.fieldnames)
            writer.writeheader()
            csvfile.seek(0)
            for row in reader:
                if row['file_identifier'] in metadata_matches:
                    writer.writerow(row)
