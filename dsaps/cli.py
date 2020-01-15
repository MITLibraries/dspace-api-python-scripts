import datetime
import logging
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
@click.pass_context
def newcoll(ctx, comm_handle, coll_name):
    client = ctx.obj['client']
    coll_id = client.post_coll_to_comm(comm_handle, coll_name)
    logger.info(coll_id)
    # STEPS TO ADD
    # post items to collections
        # post bistreams to item_links
        # post prov notes


if __name__ == '__main__':
    main()
