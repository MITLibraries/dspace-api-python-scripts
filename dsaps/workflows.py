import glob
import os

import structlog

from dsaps import helpers, models

logger = structlog.get_logger()


def append_items_to_coll(client, coll_handle, ingest_type, file_path,
                         file_type, json_metadata, ingest_data, ingest_report):
    """Append items to an existing collection."""
    coll_id = client.get_id_from_handle(coll_handle)
    items = populate_coll(client, ingest_type, file_path, file_type,
                          json_metadata, ingest_report, coll_id, ingest_data)
    for item in items:
        yield item


def populate_coll(client, ingest_type, file_path, file_type, json_metadata,
                  ingest_report, coll_id, ingest_data):
    """Populates collection with item records."""
    file_dict = {}
    if ingest_type == 'local':
        files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
        for file in files:
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_dict[file_name] = file
    elif ingest_type == 'remote':
        file_dict = helpers.build_file_dict_remote(file_path, file_type,
                                                   file_dict)
    for item_metadata in json_metadata:
        item = models.Item()
        item.metadata = item_metadata
        if ingest_report:
            for element in [e for e in item_metadata['metadata']
                            if e['key'] == 'dc.relation.isversionof']:
                ingest_report_id = element['value']
        else:
            ingest_report_id = ''
        for element in [e for e in item_metadata['metadata']
                        if e['key'] == 'file_identifier']:
            file_identifier = element['value']
            item_metadata['metadata'].remove(element)
        sel_bitstreams = helpers.select_bitstreams(ingest_type, file_dict,
                                                   file_identifier)
        item.bitstreams = sel_bitstreams
        if sel_bitstreams != []:
            item = client.post_item_to_coll(coll_id, item, ingest_data,
                                            ingest_type, ingest_report_id)
        yield item


def populate_new_coll(client, comm_handle, coll_name, ingest_type, file_path,
                      file_type, json_metadata, ingest_report, ingest_data):
    """Creates a new collection and populates it with item records."""
    coll_id = client.post_coll_to_comm(comm_handle, coll_name)
    items = populate_coll(client, ingest_type, file_path, file_type,
                          json_metadata, ingest_report, coll_id, ingest_data)
    for item in items:
        yield item


def reconcile_files_and_metadata(metadata_csv, output_path, file_path,
                                 file_type):
    """Runs a reconciliation of files and metadata."""
    file_dict = helpers.create_file_dict(file_path, file_type)
    file_ids = file_dict.keys()
    metadata_ids = helpers.create_metadata_id_list(metadata_csv)
    metadata_matches = helpers.match_metadata_to_files(file_dict, metadata_ids)
    file_matches = helpers.match_files_to_metadata(file_dict, metadata_ids)
    no_files = set(metadata_ids) - set(metadata_matches)
    no_metadata = set(file_ids) - set(file_matches)
    helpers.create_csv_from_list(no_metadata, f'{output_path}no_metadata')
    helpers.create_csv_from_list(no_files, f'{output_path}no_files')
    helpers.create_csv_from_list(metadata_matches,
                                 f'{output_path}metadata_matches')
    helpers.update_metadata_csv(metadata_csv, output_path, metadata_matches)
