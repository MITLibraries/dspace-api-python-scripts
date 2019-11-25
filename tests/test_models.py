import attr
import pytest
import requests_mock

from dsaps import models


@pytest.fixture
def client():
    with requests_mock.Mocker() as m:
        uri1 = 'mock://example.com/rest/login'
        uri2 = 'mock://example.com/rest/status'
        cookies = {'JSESSIONID': '11111111'}
        json_object = {'fullname': 'User Name'}
        m.post(uri1, cookies=cookies)
        m.get(uri2, json=json_object)
        client = models.Client('mock://example.com', 'test', 'test')
        return client


def test_get_record(client):
    """Test get_record function."""
    with requests_mock.Mocker() as m:
        uri = '/rest/items/123?expand=all'
        json_object = {'metadata': {'title': 'Sample title'}, 'type': 'item'}
        m.get(uri, json=json_object)
        rec_obj = client.get_record('123', 'items')
        assert attr.asdict(rec_obj)['metadata'] == json_object['metadata']


# def test_filtered_item_search(client):
#     """Test filtered_item_search function."""
#     item_links = client.filtered_item_search(key, string, query_type,
#                                              selected_collections='')
#     assert False
#
#
# def test__pop_inst(client):
#     rec_obj = client._pop_inst(class_type, rec_obj)
#     assert False
#
#
# def test__build_uuid_list(client):
#     child_list = client._build_uuid_list(self, rec_obj, kwargs, children)
#     assert False
