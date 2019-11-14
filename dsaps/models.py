import datetime
from functools import partial
import operator
import requests
import time

import attr

op = operator.attrgetter('name')
Field = partial(attr.ib, default=None)


class Client:
    def __init__(self, url, email, password):
        self.url = url
        print('Initializing client')
        data = {'email': email, 'password': password}
        header = {'content-type': 'application/json', 'accept':
                  'application/json'}
        session = requests.post(self.url + '/rest/login', headers=header,
                                params=data).cookies['JSESSIONID']
        cookies = {'JSESSIONID': session}
        status = requests.get(self.url + '/rest/status', headers=header,
                              cookies=cookies).json()
        self.user_full_name = status['fullname']
        self.cookies = cookies
        self.header = header
        print(f'Authenticated to {self.url} as 'f'{self.user_full_name}')

    def get_record(self, uuid, rec_type):
        """Retrieve an individual record of a particular type."""
        url = f'{self.url}/rest/{rec_type}/{uuid}?expand=all'
        record = requests.get(url, headers=self.header,
                              cookies=self.cookies).json()
        if rec_type == 'items':
            rec_obj = self._pop_inst(Item, record)
        elif rec_type == 'communities':
            rec_obj = self._pop_inst(Community, record)
        elif rec_type == 'collections':
            rec_obj = self._pop_inst(Collection, record)
        else:
            print('Invalid record type.')
            exit()
        return rec_obj

    def filtered_item_search(self, key, string, query_type,
                             selected_collections=''):
        offset = 0
        items = ''
        item_links = []
        while items != []:
            endpoint = f'{self.url}/rest/filtered-items?query_field[]='
            endpoint += f'{key}&query_op[]={query_type}&query_val[]={string}'
            endpoint += f'{selected_collections}&limit=200&offset={offset}'
            print(endpoint)
            response = requests.get(endpoint, headers=self.header,
                                    cookies=self.cookies).json()
            items = response['items']
            for item in items:
                item_links.append(item['link'])
            offset = offset + 200
        return item_links

    def _pop_inst(self, class_type, rec_obj):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(class_type)]
        kwargs = {k: v for k, v in rec_obj.items() if k in fields}
        kwargs['objtype'] = rec_obj['type']
        if class_type == Community:
            collections = self._build_uuid_list(rec_obj, kwargs, 'collections')
            rec_obj['collections'] = collections
        elif class_type == Collection:
            items = self._build_uuid_list(rec_obj, kwargs, 'items')
            rec_obj['items'] = items
        rec_obj = class_type(**kwargs)
        return rec_obj

    def _build_uuid_list(self, rec_obj, kwargs, children):
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


def elapsed_time(start_time, label):
    """Calculate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - start_time)
    print(f'{label} : {td}')
