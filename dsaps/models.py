import csv
import datetime
from functools import partial
import operator
import os
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
        """Authenticate user to DSpace API."""
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
        """Performs a search against the filtered items endpoint."""
        offset = 0
        items = ''
        item_links = []
        while items != []:
            endpoint = f'{self.url}/filtered-items?'
            params = {'query_field[]': key, 'query_op[]': query_type,
                      'query_val[]': string, '&collSel[]':
                      selected_collections, 'limit': 200, 'offset': offset}
            logger.info(params)
            response = requests.get(endpoint, headers=self.header,
                                    params=params, cookies=self.cookies)
            logger.info(f'Response url: {response.url}')
            response = response.json()
            items = response['items']
            for item in items:
                item_links.append(item['link'])
            offset = offset + 200
        return item_links

    def get_id_from_handle(self, handle):
        """Posts a collection to a specified community."""
        endpoint = f'{self.url}/handle/{handle}'
        rec_obj = requests.get(endpoint, headers=self.header,
                               cookies=self.cookies).json()
        return rec_obj['uuid']

    def post_coll_to_comm(self, comm_handle, coll_name):
        """Posts a collection to a specified community."""
        endpoint = f'{self.url}/handle/{comm_handle}'
        community = requests.get(endpoint, headers=self.header,
                                 cookies=self.cookies).json()
        comm_id = community['uuid']
        collection = {'name': coll_name}
        endpoint2 = f'{self.url}/communities/{comm_id}/collections'
        coll_id = requests.post(endpoint2, headers=self.header,
                                cookies=self.cookies, json=collection).json()
        coll_id = coll_id['uuid']
        logger.info(f'Collection posted: {coll_id}')
        return coll_id

    def post_items_to_coll(self, coll_id, coll_metadata, file_dict,
                           ingest_type):
        """Posts items to a specified collection."""
        for item_metadata in coll_metadata:
            file_exists = ''
            for element in [e for e in item_metadata['metadata']
                            if e['key'] == 'file_identifier']:
                file_identifier = element['value']
                item_metadata['metadata'].remove(element)
            for k in [e for e in file_dict if file_identifier in e]:
                file_exists = True
            if file_exists is True:
                endpoint = f'{self.url}/collections/{coll_id}/items'
                item_id = requests.post(endpoint, headers=self.header,
                                        cookies=self.cookies,
                                        json=item_metadata).json()
                item_id = item_id['uuid']
                bit_ids = self.post_bitstreams_to_item(item_id,
                                                       file_identifier,
                                                       file_dict, ingest_type)
                for bit_id in bit_ids:
                    logger.info(f'Bitstream posted: {bit_id}')
            yield item_id

    def post_bitstreams_to_item(self, item_id, file_identifier, file_dict,
                                ingest_type):
        """Posts bitstreams to a specified item."""
        for k, v in file_dict.items():
            bitstreams = []
            if k.startswith(file_identifier):
                bitstreams.append(k)
            bitstreams.sort()
            for bitstream in bitstreams:
                bitstream_path = file_dict[bitstream]
                file_name = os.path.basename(bitstream_path)
                if ingest_type == 'local':
                    data = open(bitstream_path, 'rb')
                elif ingest_type == 'remote':
                    data = requests.get(bitstream_path)
                endpoint = (f'{self.url}/items/{item_id}'
                            + f'/bitstreams?name={file_name}')
                header_upload = {'accept': 'application/json'}
                bit_id = requests.post(endpoint, headers=header_upload,
                                       cookies=self.cookies, data=data).json()
                bit_id = bit_id['uuid']
                yield bit_id

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
        """Builds a list of the uuids for an object's children."""
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


def build_file_dict_remote(directory_url, file_type, file_dict):
    """Build list of files in a remote directory."""
    response = requests.get(directory_url)
    links = html.fromstring(response.content).iterlinks()
    for link in [i for i in links if i[2].endswith(file_type)]:
        file_identifier = link[2].replace(f'.{file_type}', '')
        file_dict[file_identifier] = f'{directory_url}{link[2]}'
    return file_dict


def create_csv_from_list(list_name, output):
    """Creates CSV file from list content."""
    with open(output, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['id'])
        for item in list_name:
            writer.writerow([item])


def elapsed_time(start_time, label):
    """Calculate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - start_time)
    logger.info(f'{label} : {td}')


def metadata_csv(row, key, field, language=None, delimiter=''):
    """Create metadata element from CSV."""
    metadata_elems = []
    if row[field] != '':
        if delimiter != '' and delimiter in row[field]:
            values = row[field].split(delimiter)
            for value in values:
                if language is not None:
                    metadata_elem = {'key': key, 'language': language, 'value':
                                     value}
                    metadata_elems.append(metadata_elem)
                else:
                    metadata_elem = {'key': key, 'value': value}
                    metadata_elems.append(metadata_elem)
        else:
            value = row[field]
            if language is not None:
                metadata_elem = {'key': key, 'language': language, 'value':
                                 value}
            else:
                metadata_elem = {'key': key, 'value': value}
            metadata_elems.append(metadata_elem)
    return metadata_elems


def create_metadata_rec(mapping_dict, row, metadata_rec):
    """Create metadata record from CSV."""
    for k, v in mapping_dict.items():
        if len(v) == 3:
            metadata_elems = metadata_csv(row, k, v[0], v[1], v[2])
        else:
            metadata_elems = metadata_csv(row, k, v[0])
        for metadata_elem in metadata_elems:
            metadata_rec.append(metadata_elem)
    return metadata_rec
