import datetime
from functools import partial
import operator
import requests
import time

import attr
from lxml import html
import structlog

op = operator.attrgetter('name')
Field = partial(attr.ib, default=None)

logger = structlog.get_logger()


class Client:
    def __init__(self, url):
        header = {'content-type': 'application/json', 'accept':
                  'application/json'}
        self.url = url.rstrip('/')
        self.cookies = None
        self.header = header
        logger.info('Initializing client')

    def authenticate(self, email, password):
        header = self.header
        data = {'email': email, 'password': password}
        session = requests.post(f'{self.url}/login', headers=header,
                                params=data).cookies['JSESSIONID']
        cookies = {'JSESSIONID': session}
        status = requests.get(f'{self.url}/status', headers=header,
                              cookies=cookies).json()
        self.user_full_name = status['fullname']
        self.cookies = cookies
        self.header = header
        logger.info(f'Authenticated to {self.url} as 'f'{self.user_full_name}')

    def get_record(self, uuid, rec_type):
        """Retrieve an individual record of a particular type."""
        url = f'{self.url}/{rec_type}/{uuid}?expand=all'
        record = requests.get(url, headers=self.header,
                              cookies=self.cookies).json()
        if rec_type == 'items':
            rec_obj = self._pop_inst(Item, record)
        elif rec_type == 'communities':
            rec_obj = self._pop_inst(Community, record)
        elif rec_type == 'collections':
            rec_obj = self._pop_inst(Collection, record)
        else:
            logger.info('Invalid record type.')
            exit()
        return rec_obj

    def filtered_item_search(self, key, string, query_type,
                             selected_collections=''):
        offset = 0
        items = ''
        item_links = []
        while items != []:
            endpoint = f'{self.url}/filtered-items?'
            params = {'query_field[]': key, 'query_op[]': query_type,
                      'query_val[]': string, '&collSel[]':
                      selected_collections, 'limit': 200, 'offset': offset}
            logger.info(params)
            print(endpoint)
            response = requests.get(endpoint, headers=self.header,
                                    params=params, cookies=self.cookies)
            print(f'Response url: {response.url}')
            response = response.json()
            items = response['items']
            for item in items:
                item_links.append(item['link'])
            offset = offset + 200
        return item_links

    def post_coll_to_comm(self, comm_handle, coll_name):
        endpoint = f'{self.url}/handle/{comm_handle}'
        community = requests.get(endpoint, headers=self.header,
                                 cookies=self.cookies).json()
        comm_id = community['uuid']
        collection = {'name': coll_name}
        endpoint2 = f'{self.url}/communities/{comm_id}/collections'
        coll_id = requests.post(endpoint2, headers=self.header,
                                cookies=self.cookies, json=collection).json()
        return coll_id['link']

    def _pop_inst(self, class_type, rec_obj):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(class_type)]
        kwargs = {k: v for k, v in rec_obj.items() if k in fields}
        kwargs['objtype'] = rec_obj['type']
        if class_type == Community:
            collections = self._build_uuid_list(rec_obj, kwargs, 'collections')
            rec_obj['collections'] = collections
        elif class_type == Collection:
            items = self._build_uuid_list(rec_obj, 'items')
            rec_obj['items'] = items
        rec_obj = class_type(**kwargs)
        return rec_obj

    def _build_uuid_list(self, rec_obj, children):
        child_list = []
        for child in rec_obj[children]:
            child_list.append(child['uuid'])
        return child_list


@attr.s
class BaseRecord:
    uuid = Field()
    name = Field()
    handle = Field()
    link = Field()
    objtype = Field()


@attr.s
class Item(BaseRecord):
    metadata = Field()
    bitstreams = Field()


@attr.s
class Community(BaseRecord):
    collections = Field()


@attr.s
class Collection(BaseRecord):
    items = Field()


@attr.s
class MetadataEntry(BaseRecord):
    key = Field()
    value = Field()
    language = Field()


def build_file_list_remote(directory_url, file_extension):
    """Build list of files in local directory."""
    file_list = {}
    response = requests.get(directory_url)
    links = html.fromstring(response.content).iterlinks()
    for link in links:
        if link[2].endswith(file_extension):
            file_list[link[2]] = f'{directory_url}{link[2]}'
    return file_list


def elapsed_time(start_time, label):
    """Calculate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - start_time)
    logger.info(f'{label} : {td}')
