import time

import click

from dsaps import models


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
    print('Application start')
    client = models.Client(url, email, password)
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
    print(item_links)
    models.elapsed_time(start_time, 'Elapsed time')


if __name__ == '__main__':
    main()
