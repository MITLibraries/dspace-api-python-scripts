import csv
import datetime
import json
import logging
import os
import time

import click
import structlog

from dsaps.models import Client, Collection
from dsaps import helpers

logger = structlog.get_logger()


@click.group(chain=True)
@click.option('--url', envvar='DSPACE_URL')
@click.option('-e', '--email', envvar='TEST_EMAIL',
              help='The email of the user for authentication.')
@click.option('-p', '--password', envvar='TEST_PASS',
              hide_input=True, help='The password for authentication.')
@click.pass_context
def main(ctx, url, email, password):
    ctx.obj = {}
    if os.path.isdir('logs') is False:
        os.mkdir('logs')
    dt = datetime.datetime.utcnow().isoformat(timespec='seconds')
    log_suffix = f'{dt}.log'
    structlog.configure(processors=[
                        structlog.stdlib.filter_by_level,
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.PositionalArgumentsFormatter(),
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer()
                        ],
                        context_class=dict,
                        logger_factory=structlog.stdlib.LoggerFactory())
    logging.basicConfig(format="%(message)s",
                        handlers=[logging.FileHandler(f'logs/log-{log_suffix}',
                                  'w')],
                        level=logging.INFO)
    logger.info('Application start')
    client = Client(url)
    client.authenticate(email, password)
    start_time = time.time()
    ctx.obj['client'] = client
    ctx.obj['start_time'] = start_time
    ctx.obj['log_suffix'] = log_suffix


@main.command()
@click.option('-m', '--metadata-csv', required=True,
              help='The full path to the CSV file of metadata for the items.')
@click.option('--field-map', required=True,
              help='Path to JSON field mapping file')
@click.option('-d', '--directory', required=True,
              help='The full path to the content, either a directory of files '
              'or a URL for the storage location.')
@click.option('-t', '--file-type',
              help='The file type to be uploaded, if limited to one file '
              'type.', default='*')
@click.option('-r', '--ingest-report', is_flag=True,
              help='Create ingest report for updating other systems.')
@click.pass_context
def additems(ctx, metadata_csv, field_map, directory, file_type,
             ingest_report):
    client = ctx.obj['client']
    start_time = ctx.obj['start_time']
    collection_uuid = ctx.obj['collection_uuid']
    with open(metadata_csv, 'r') as csvfile, open(field_map, 'r') as jsonfile:
        metadata = csv.DictReader(csvfile)
        mapping = json.load(jsonfile)
        collection = Collection.from_csv(metadata, mapping)
    for item in collection.items:
        item.bitstreams_from_directory(directory, file_type)
    collection.uuid = collection_uuid
    items = collection.post_items(client)
    if ingest_report:
        report_name = metadata_csv.replace('.csv', '-ingest.csv')
        helpers.create_ingest_report(items, report_name)
    helpers.elapsed_time(start_time, 'Total runtime:')


@main.command()
@click.option('-c', '--collection-handle', required=True,
              help='The handle of the collection to which items are being '
              'added.')
@click.pass_context
def existingcollection(ctx, collection_handle):
    client = ctx.obj['client']
    collection_uuid = client.get_id_from_handle(collection_handle)
    ctx.obj['collection_uuid'] = collection_uuid


@main.command()
@click.option('-c', '--community-handle', required=True,
              help='The handle of the community in which to create the ,'
              'collection.')
@click.option('-n', '--collection-name', required=True,
              help='The name of the collection to be created.')
@click.pass_context
def newcollection(ctx, community_handle, collection_name):
    client = ctx.obj['client']
    collection_uuid = client.post_coll_to_comm(community_handle,
                                               collection_name)
    ctx.obj['collection_uuid'] = collection_uuid


# @main.command()
# @click.option('-m', '--metadata_csv', prompt='Enter the metadata CSV file',
#               help='The path of the CSV file of metadata.')
# @click.option('-o', '--output_path', prompt='Enter the output path',
#               default='', help='The path of the output files, include '
#               '/ at the end of the path')
# @click.option('-f', '--file_path', prompt='Enter the path',
#               help='The path of the content, a URL or local drive path.'
#               'Include / at the end of a local drive path.')
# @click.option('-t', '--file_type', prompt='Enter the file type',
#               help='The file type to be uploaded.')
# def reconcile(metadata_csv, file_path, file_type, output_path):
#     workflows.reconcile_files_and_metadata(metadata_csv, output_path,
#                                            file_path, file_type)


if __name__ == '__main__':
    main()
