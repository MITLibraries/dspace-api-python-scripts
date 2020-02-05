import datetime
import glob
import json
import logging
import os
import time

import click
import structlog

from dsaps import models

logger = structlog.get_logger()


@click.group()
@click.option('--url', envvar='DSPACE_URL')
@click.option('-e', '--email', prompt='Enter email',
              help='The email of the user for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              envvar='TEST_PASS', hide_input=True,
              help='The password for authentication.')
@click.pass_context
def main(ctx, url, email, password):
    ctx.obj = {}
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


@main.command()
@click.option('-f', '--field', prompt='Enter the field to be searched',
              help='The field to search.')
@click.option('-s', '--string', prompt='Enter the string',
              help='The field to search.')
@click.option('-t', '--search_type', prompt='Enter the type of search',
              help='The type of search.',
              type=click.Choice(['exists', 'doesnt_exist', 'equals',
                                 'not_equals', 'contains', 'doesnt_contain']),
              default='contains')
@click.pass_context
def search(ctx, field, string, search_type):
    # Temp function for testing
    client = ctx.obj['client']
    start_time = ctx.obj['start_time']
    item_links = client.filtered_item_search(field, string, search_type)
    logger.info(item_links)
    models.elapsed_time(start_time, 'Elapsed time')


@main.command()
@click.option('-c', '--comm_handle', prompt='Enter the community handle',
              help='The handle of the community in which to create the ,'
              'collection.')
@click.option('-n', '--coll_name', prompt='Enter the name of the collection',
              help='The name of the collection to be created.')
@click.option('-m', '--metadata', prompt='Enter the path of the metadata file',
              help='The path of the JSON file of metadata.')
@click.option('-f', '--file_path', prompt='Enter the path',
              help='The path of the content, a URL or local drive path.')
@click.option('-t', '--file_type', prompt='Enter the file type',
              help='The file type to be uploaded.')
@click.option('-i', '--ingest_type', prompt='Enter the type of ingest',
              help='The type of ingest to perform: local, remote.',
              type=click.Choice(['local', 'remote']))
@click.pass_context
def newcoll(ctx, comm_handle, coll_name, metadata, file_path, file_type,
            ingest_type):
    client = ctx.obj['client']
    start_time = ctx.obj['start_time']
    with open(metadata, encoding='UTF-8') as fp:
        coll_metadata = json.load(fp)
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
        items = client.post_items_to_coll(coll_id, coll_metadata, file_dict,
                                          ingest_type)
        for item in items:
            logger.info(f'Item posted: {item}')
    models.elapsed_time(start_time, 'Total runtime:')


if __name__ == '__main__':
    main()
