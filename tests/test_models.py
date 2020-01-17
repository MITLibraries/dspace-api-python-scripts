import attr
import pytest
import requests_mock

from dsaps import models


@pytest.fixture
def client():
    client = models.Client('mock://example.com/')
    client.header = {}
    client.cookies = {}
    client.user_full_name = ''
    return client


@pytest.fixture
def sample_content(tmp_path):
    content = 'test'
    dir = tmp_path / 'sub'
    dir.mkdir()
    sample_content = dir / '123.pdf'
    sample_content.write_text(content)
    return sample_content


def test_authenticate(client):
    """Test authenticate function."""
    with requests_mock.Mocker() as m:
        email = 'test@test.mock'
        password = '1234'
        cookies = {'JSESSIONID': '11111111'}
        json_object = {'fullname': 'User Name'}
        m.post('mock://example.com/login', cookies=cookies)
        m.get('mock://example.com/status', json=json_object)
        client.authenticate(email, password)
        assert client.user_full_name == 'User Name'
        assert client.cookies == cookies


def test_get_record(client):
    """Test get_record function."""
    with requests_mock.Mocker() as m:
        uri = 'mock://example.com/items/123?expand=all'
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
        endpoint = 'mock://example.com/filtered-items?'
        json_object_1 = {'items': [{'link': '1234'}]}
        json_object_2 = {'items': []}
        m.get(endpoint, [{'json': json_object_1}, {'json': json_object_2}])

        item_links = client.filtered_item_search(key, string, query_type,
                                                 selected_collections='')
        assert '1234' in item_links


def test_post_coll_to_comm(client):
    """Test post_coll_to_comm function."""
    with requests_mock.Mocker() as m:
        comm_handle = '1234'
        coll_name = 'Test Collection'
        json_object_1 = {'uuid': 'a1b2'}
        json_object_2 = {'uuid': '5678'}
        m.get('mock://example.com/handle/1234', json=json_object_1)
        m.post('mock://example.com/communities/a1b2/collections',
               json=json_object_2)
        coll_id = client.post_coll_to_comm(comm_handle, coll_name)
        assert coll_id == '5678'


def test_post_items_to_coll(client, sample_content):
    """Test post_items_to_coll function."""
    with requests_mock.Mocker() as m:
        coll_metadata = [{"metadata": [
                         {"key": "file_identifier",
                          "value": "123"},
                         {"key": "dc.title", "value":
                          "Monitoring Works: Getting Teachers",
                          "language": "en_US"}]}]
        coll_id = '789'
        ingest_type = 'local'
        file_dict = {'123': sample_content}
        json_object_1 = {'uuid': 'a1b2'}
        m.post('mock://example.com/collections/789/items', json=json_object_1)
        url = 'mock://example.com/items/a1b2/bitstreams?name=123.pdf'
        json_object_2 = {'uuid': 'c3d4'}
        m.post(url, json=json_object_2)
        item_ids = client.post_items_to_coll(coll_id, coll_metadata, file_dict,
                                             ingest_type)
        for item_id in item_ids:
            assert 'a1b2' == item_id


def test_post_bitstreams_to_item(client, sample_content):
    """Test post_bitstreams_to_item function."""
    with requests_mock.Mocker() as m:
        item_id = 'a1b2'
        ingest_type = 'local'
        file_identifier = '123'
        file_dict = {'123': sample_content}
        json_object_1 = {'uuid': 'c3d4'}
        url = 'mock://example.com/items/a1b2/bitstreams?name=123.pdf'
        m.post(url, json=json_object_1)
        bit_ids = client.post_bitstreams_to_item(item_id, file_identifier,
                                                 file_dict, ingest_type)
        for bit_id in bit_ids:
            assert 'c3d4' == bit_id


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


def test_build_file_dict_remote():
    """Test build_file_dict_remote function."""
    content = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>'
    content += '<head><title>Index of /pdf</title></head><body><h1>Index of /'
    content += 'pdf</h1><table><tr><th>Name</th><th>Last modified</th><th>'
    content += 'Size</th></tr><tr><td><a href="999.pdf">999.pdf</a></td><td>'
    content += '2001-02-16 11:59 </td><td>107K</td></tr></table></body></html>'
    with requests_mock.Mocker() as m:
        directory_url = 'mock://test.com/pdfs/'
        file_type = 'pdf'
        file_dict = {}
        m.get(directory_url, text=content)
        file_list = models.build_file_dict_remote(directory_url, file_type,
                                                  file_dict)
        assert '999' in file_list
