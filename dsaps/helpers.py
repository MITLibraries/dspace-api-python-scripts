import collections
import csv
import datetime
import glob
import os
import requests
import time

from lxml import html
import structlog


logger = structlog.get_logger()


def build_file_dict_remote(directory_url, file_type, file_dict):
    """Build list of files in a remote directory."""
    response = requests.get(directory_url)
    links = html.fromstring(response.content).iterlinks()
    for link in [i for i in links if i[2].endswith(file_type)]:
        file_identifier = link[2].replace(f'.{file_type}', '')
        file_dict[file_identifier] = f'{directory_url}{link[2]}'
    return file_dict


def create_csv_from_list(list_name, output):
    """Creates CSV file from list content."""
    with open(f'{output}.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id'])
        for item in list_name:
            writer.writerow([item])


def create_file_dict(file_path, file_type):
    """Creates a dict of file IDs and file paths."""
    if file_path.startswith('http'):
        file_dict = build_file_dict_remote(file_path, file_type, {})
    else:
        files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
        file_dict = {}
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_dict[file_name] = file
    return file_dict


def create_ingest_report(ingest_data, file_name):
    """Creates ingest report of handles and DOS links."""
    with open(f'{file_name}.csv', 'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(['uri'] + ['link'])
        for uri, handle in ingest_data.items():
            writer.writerow([uri] + [f'https://hdl.handle.net/{handle}'])


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


def select_bitstreams(ingest_type, file_dict, file_identifier):
    """Select the appropriate bitstreams for posting to an item."""
    sel_bitstreams = []
    file_dict = collections.OrderedDict(sorted(file_dict.items()))
    for k in [e for e in file_dict if e.startswith(file_identifier)]:
        pass
    for bitstream_id in [k for k, v in file_dict.items()
                         if k.startswith(file_identifier)]:
        if ingest_type == 'local':
            data = open(file_dict[bitstream_id], 'rb')
        elif ingest_type == 'remote':
            data = requests.get(file_dict[bitstream_id]).content
        sel_bitstreams.append(data)
    return sel_bitstreams


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
