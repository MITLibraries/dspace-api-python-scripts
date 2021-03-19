import csv
import glob
import os

from dsaps import models


def create_file_dict(file_path, file_type):
    """Creates a dict of file IDs and file paths."""
    if file_path.startswith('http'):
        file_dict = models.build_file_dict_remote(file_path, file_type, {})
    else:
        files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
        file_dict = {}
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_dict[file_name] = file
    return file_dict


def create_json_metadata(metadata_csv, multiple_terms):
    """Creates JSON metadata from a CSV."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        metadata_group = []
        mapping_dict = {'file_identifier': ['file_identifier'],
                        'dc.title': ['title', 'en_US'],
                        'dc.relation.isversionof': ['uri']}
        for row in reader:
            metadata_rec = []
            if multiple_terms == 'delimited':
                metadata_rec = models.create_metadata_rec(mapping_dict, row,
                                                          metadata_rec)
            else:
                for csv_key, csv_value in row.items():
                    if csv_value is not None:
                        if csv_key[-1].isdigit():
                            dc_key = csv_key[:-2]
                        else:
                            dc_key = csv_key
                        if dc_key not in ['dc.contributor.author',
                                          'dc.date.issued', 'file_identifier']:
                            metadata_elems = models.metadata_csv(row, dc_key,
                                                                 csv_key,
                                                                 'en_US')
                        else:
                            metadata_elems = models.metadata_csv(row, dc_key,
                                                                 csv_key)
                        for metadata_elem in metadata_elems:
                            metadata_rec.append(metadata_elem)
            item = {'metadata': metadata_rec}
            metadata_group.append(item)
        return metadata_group


def create_metadata_id_list(metadata_csv):
    """Creates a list of IDs from a metadata CSV"""
    metadata_ids = []
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in [r for r in reader if r['file_identifier'] != '']:
            metadata_ids.append(row['file_identifier'])
    return metadata_ids


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


def populate_new_coll(client, comm_handle, coll_name, metadata, file_path,
                      file_type, ingest_type, ingest_data, ingest_report):
    """Creates a new collection and populates it with item records."""
    coll_id = client.post_coll_to_comm(comm_handle, coll_name)
    file_dict = {}
    if ingest_type == 'local':
        files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_dict[file_name] = file
    elif ingest_type == 'remote':
        file_dict = models.build_file_dict_remote(file_path, file_type,
                                                  file_dict)
    items = client.post_items_to_coll(coll_id, metadata, file_dict,
                                      ingest_type, ingest_data,
                                      ingest_report)
    for item in items:
        yield item


def reconcile_files_and_metadata(metadata_csv, output_path, file_path,
                                 file_type):
    """Runs a reconciliation of files and metadata."""
    file_dict = create_file_dict(file_path, file_type)
    file_ids = file_dict.keys()
    metadata_ids = create_metadata_id_list(metadata_csv)
    metadata_matches = match_metadata_to_files(file_dict, metadata_ids)
    file_matches = match_files_to_metadata(file_dict, metadata_ids)
    no_files = set(metadata_ids) - set(metadata_matches)
    no_metadata = set(file_ids) - set(file_matches)
    models.create_csv_from_list(no_metadata, f'{output_path}no_metadata')
    models.create_csv_from_list(no_files, f'{output_path}no_files')
    models.create_csv_from_list(metadata_matches,
                                f'{output_path}metadata_matches')
    update_metadata_csv(metadata_csv, output_path, metadata_matches)


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
