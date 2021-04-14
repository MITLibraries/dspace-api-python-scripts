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

cwd = os.getcwd()


def validate_path(ctx, param, value):
    """Validates th formatting of The submitted path"""
    if value[-1] == '/':
        return value
    else:
        raise click.BadParameter('Include / at the end of the path.')


@click.group(chain=True)
@click.option('--url', envvar='DSPACE_URL', required=True,)
@click.option('-e', '--email', envvar='TEST_EMAIL', required=True,
              help='The email of the user for authentication.')
@click.option('-p', '--password', envvar='TEST_PASS', required=True,
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
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='The path to the CSV file of metadata for the items.')
@click.option('--field-map', required=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='The path to JSON field mapping file.')
@click.option('-d', '--content-directory', required=True,
              type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help='The full path to the content, either a directory of files '
              'or a URL for the storage location.')
@click.option('-t', '--file-type',
              help='The file type to be uploaded, if limited to one file '
              'type.', default='*')
@click.option('-r', '--ingest-report', is_flag=True,
              help='Create ingest report for updating other systems.')
@click.option('-c', '--collection-handle',
              help='The handle of the collection to which items are being '
              'added.', default=None)
@click.pass_context
def additems(ctx, metadata_csv, field_map, content_directory, file_type,
             ingest_report, collection_handle):
    """Adds items to a specified collection from a metadata CSV, a field
     mapping file, and a directory of files. May be run in conjunction with the
     newcollection CLI command."""
    client = ctx.obj['client']
    start_time = ctx.obj['start_time']
    if 'collection_uuid' not in ctx.obj and collection_handle is None:
        raise click.UsageError('collection_handle option must be used or '
                               'additems must be run after newcollection '
                               'command.')
    elif 'collection_uuid' in ctx.obj:
        collection_uuid = ctx.obj['collection_uuid']
    else:
        collection_uuid = client.get_uuid_from_handle(collection_handle)
    with open(metadata_csv, 'r') as csvfile, open(field_map, 'r') as jsonfile:
        metadata = csv.DictReader(csvfile)
        mapping = json.load(jsonfile)
        collection = Collection.from_csv(metadata, mapping)
    for item in collection.items:
        item.bitstreams_from_directory(content_directory, file_type)
    collection.uuid = collection_uuid
    items = collection.post_items(client)
    if ingest_report:
        report_name = metadata_csv.replace('.csv', '-ingest.csv')
        helpers.create_ingest_report(items, report_name)
    elapsed_time = datetime.timedelta(seconds=time.time() - start_time)
    logger.info(f'Total runtime : {elapsed_time}')


@main.command()
@click.option('-c', '--community-handle', required=True,
              help='The handle of the community in which to create the ,'
              'collection.')
@click.option('-n', '--collection-name', required=True,
              help='The name of the collection to be created.')
@click.pass_context
def newcollection(ctx, community_handle, collection_name):
    """Posts a new collection to a specified community. Used in conjunction
     with the additems CLI command to populate the new collection with
     items."""
    client = ctx.obj['client']
    collection_uuid = client.post_coll_to_comm(community_handle,
                                               collection_name)
    ctx.obj['collection_uuid'] = collection_uuid


@main.command()
@click.option('-m', '--metadata-csv', required=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='The path of the CSV file of metadata.')
@click.option('-o', '--output-directory',
              type=click.Path(exists=True, dir_okay=True, file_okay=False),
              default=f'{cwd}/', callback=validate_path,
              help='The path of the output files, include / at the end of the '
              'path.')
@click.option('-d', '--content-directory', required=True,
              help='The full path to the content, either a directory of files '
              'or a URL for the storage location.')
@click.option('-t', '--file-type',
              help='The file type to be uploaded, if limited to one file '
              'type.', default='*')
def reconcile(metadata_csv, output_directory, content_directory, file_type):
    """Runs a reconciliation of the specified files and metadata that produces
     reports of files with no metadata, metadata with no files, metadata
     matched to files, and an updated version of the metadata CSV with only
     the records that have matching files."""
    file_ids = helpers.create_file_list(content_directory, file_type)
    metadata_ids = helpers.create_metadata_id_list(metadata_csv)
    metadata_matches = helpers.match_metadata_to_files(file_ids, metadata_ids)
    file_matches = helpers.match_files_to_metadata(file_ids, metadata_ids)
    no_files = set(metadata_ids) - set(metadata_matches)
    no_metadata = set(file_ids) - set(file_matches)
    helpers.create_csv_from_list(no_metadata, f'{output_directory}no_metadata')
    helpers.create_csv_from_list(no_files, f'{output_directory}no_files')
    helpers.create_csv_from_list(metadata_matches,
                                 f'{output_directory}metadata_matches')
    helpers.update_metadata_csv(metadata_csv, output_directory,
                                metadata_matches)


if __name__ == '__main__':
    main()
