import datetime
import logging
import os
import time

import click
import structlog

from dsaps import helpers, metadata, models, workflows

logger = structlog.get_logger()


@click.group()
@click.option('--url', envvar='DSPACE_URL')
@click.option('-e', '--email', prompt='Enter email', envvar='TEST_EMAIL',
              help='The email of the user for authentication.')
@click.option('-p', '--password', prompt='Enter password', envvar='TEST_PASS',
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
    client = models.Client(url)
    client.authenticate(email, password)
    start_time = time.time()
    ctx.obj['client'] = client
    ctx.obj['start_time'] = start_time
    ctx.obj['log_suffix'] = log_suffix


@main.command()
@click.option('-c', '--coll_handle', prompt='Enter the collection handle',
              help='The handle of the collection to which items are being '
              'added.')
@click.option('-m', '--metadata_csv', prompt='Enter the metadata CSV file',
              help='The path of the CSV file of metadata.')
@click.option('-f', '--file_path', prompt='Enter the path',
              help='The path of the content, a URL or local drive path.')
@click.option('-t', '--file_type', prompt='Enter the file type',
              help='The file type to be uploaded.')
@click.option('-i', '--ingest_type', prompt='Enter the type of ingest',
              help='The type of ingest to perform: local, remote.',
              type=click.Choice(['local', 'remote']), default='remote')
@click.option('-r', '--ingest_report', prompt='Create an ingest report?',
              help='Create ingest report for updating other systems.',
              default=False)
@click.option('-u', '--multiple_terms', prompt='Method of separating terms?',
              help='The way multiple terms are separated in the metadata CSV.',
              type=click.Choice(['delimited', 'num_columns']),
              default='delimited')
@click.pass_context
def appendcoll(ctx, coll_handle, metadata_csv, file_path, file_type,
               ingest_type, ingest_report, multiple_terms):
    client = ctx.obj['client']
    start_time = ctx.obj['start_time']
    ingest_data = {}
    json_metadata = metadata.create_json_metadata(metadata_csv, multiple_terms)
    items = workflows.append_items_to_coll(client, coll_handle, ingest_type,
                                           file_path, file_type, json_metadata,
                                           ingest_data, ingest_report)
    for item in items:
        logger.info(f'Item posted: {item}')
    helpers.elapsed_time(start_time, 'Total runtime:')


@main.command()
@click.option('-c', '--comm_handle', prompt='Enter the community handle',
              help='The handle of the community in which to create the ,'
              'collection.')
@click.option('-n', '--coll_name', prompt='Enter the name of the collection',
              help='The name of the collection to be created.')
@click.option('-m', '--metadata_csv', prompt='Enter the metadata CSV file',
              help='The path of the CSV file of metadata.')
@click.option('-f', '--file_path', prompt='Enter the path',
              help='The path of the content, a URL or local drive path.')
@click.option('-t', '--file_type', prompt='Enter the file type',
              help='The file type to be uploaded.')
@click.option('-i', '--ingest_type', prompt='Enter the type of ingest',
              help='The type of ingest to perform: local, remote.',
              type=click.Choice(['local', 'remote']), default='remote')
@click.option('-r', '--ingest_report', prompt='Create an ingest report?',
              help='Create ingest report for updating other systems',
              default=False)
@click.option('-u', '--multiple_terms', prompt='Method of separating terms?',
              help='The way multiple terms are separated in the metadata CSV.',
              type=click.Choice(['delimited', 'num_columns']),
              default='delimited')
@click.pass_context
def newcoll(ctx, comm_handle, coll_name, metadata_csv, file_path, file_type,
            ingest_type, ingest_report, multiple_terms):
    client = ctx.obj['client']
    start_time = ctx.obj['start_time']
    ingest_data = {}
    json_metadata = metadata.create_json_metadata(metadata_csv, multiple_terms)
    items = workflows.populate_new_coll(client, comm_handle, coll_name,
                                        ingest_type, file_path, file_type,
                                        json_metadata, ingest_report,
                                        ingest_data)
    for item in items:
        logger.info(f'Item posted: {item}')
    if ingest_report == 'True':
        report_name = metadata_csv.replace('.csv', '-ingest.csv')
        helpers.create_ingest_report(ingest_data, report_name)
    helpers.elapsed_time(start_time, 'Total runtime:')


@main.command()
@click.option('-m', '--metadata_csv', prompt='Enter the metadata CSV file',
              help='The path of the CSV file of metadata.')
@click.option('-o', '--output_path', prompt='Enter the output path',
              default='', help='The path of the output files, include '
              '/ at the end of the path')
@click.option('-f', '--file_path', prompt='Enter the path',
              help='The path of the content, a URL or local drive path.'
              'Include / at the end of a local drive path.')
@click.option('-t', '--file_type', prompt='Enter the file type',
              help='The file type to be uploaded.')
def reconcile(metadata_csv, file_path, file_type, output_path):
    workflows.reconcile_files_and_metadata(metadata_csv, output_path,
                                           file_path, file_type)


if __name__ == '__main__':
    main()
