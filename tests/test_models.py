import pytest
import requests_mock

from dsaps import models


@pytest.fixture
def client():
    pass


# def test_get_record(client):
#     """Test get_record function."""
#     rec_obj = client.get_record(uuid, rec_type)
#     assert False


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
