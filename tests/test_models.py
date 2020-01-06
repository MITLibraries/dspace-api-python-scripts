import os

import attr
import pytest
import requests_mock

from dsaps import models


@pytest.fixture
def client():
    client = models.Client('mock://example.com')
    client.header = {}
    client.cookies = {}
    client.user_full_name = ''
    return client


def test_authenticate(client):
    """Test authenticate function."""
    with requests_mock.Mocker() as m:
        url1 = '/rest/login'
        url2 = '/rest/status'
        email = 'test@test.mock'
        password = '1234'
        header = {'content-type': 'application/json', 'accept':
                  'application/json'}
        cookies = {'JSESSIONID': '11111111'}
        json_object = {'fullname': 'User Name'}
        m.post(url1, cookies=cookies)
        m.get(url2, json=json_object)
        client.authenticate(email, password)
        assert client.user_full_name == 'User Name'
        assert client.cookies == cookies
        assert client.header == header


def test_get_record(client):
    """Test get_record function."""
    with requests_mock.Mocker() as m:
        uri = '/rest/items/123?expand=all'
        json_object = {'metadata': {'title': 'Sample title'}, 'type': 'item'}
        m.get(uri, json=json_object)
        rec_obj = client.get_record('123', 'items')
        assert attr.asdict(rec_obj)['metadata'] == json_object['metadata']


def test_filtered_item_search(client):
    """Test filtered_item_search function."""
    with requests_mock.Mocker() as m:
        key = 'dc.title'
        string = 'test'
        query_type = 'contains'
        endpoint = '/rest/filtered-items?'
        json_object_1 = {'items': [{'link': '1234'}]}
        json_object_2 = {'items': []}
        m.get(endpoint, [{'json': json_object_1}, {'json': json_object_2}])

        item_links = client.filtered_item_search(key, string, query_type,
                                                 selected_collections='')
        assert '1234' in item_links


def test__pop_inst(client):
    """Test _pop_inst function."""
    class_type = models.Collection
    rec_obj = {'name': 'Test title', 'type': 'collection', 'items': []}
    rec_obj = client._pop_inst(class_type, rec_obj)
    assert type(rec_obj) == class_type
    assert rec_obj.name == 'Test title'


def test__build_uuid_list(client):
    """Test _build_uuid_list function."""
    rec_obj = {'items': [{'uuid': '1234'}]}
    children = 'items'
    child_list = client._build_uuid_list(rec_obj, children)
    assert '1234' in child_list


def test_build_file_list_remote():
    """Test build_file_list_remote function."""
    content = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>'
    content += '<head><title>Index of /pdf</title></head><body><h1>Index of /'
    content += 'pdf</h1><table><tr><th>Name</th><th>Last modified</th><th>'
    content += 'Size</th></tr><tr><td><a href="999.pdf">999.pdf</a></td><td>'
    content += '2001-02-16 11:59 </td><td>107K</td></tr></table></body></html>'
    with requests_mock.Mocker() as m:
        directory_url = 'mock://test.com/pdfs/'
        file_extension = 'pdf'
        m.get(directory_url, text=content)
        file_list = models.build_file_list_remote(directory_url,
                                                  file_extension)
        assert '999.pdf' in file_list
