import csv

import attr
import requests_mock

from dsaps import models


def test_authenticate(client):
    """Test authenticate method."""
    email = 'test@test.mock'
    password = '1234'
    client.authenticate(email, password)
    assert client.user_full_name == 'User Name'
    assert client.cookies == {'JSESSIONID': '11111111'}


def test_get_record(client):
    """Test get_record method."""
    rec_obj = client.get_record('123', 'items')
    assert attr.asdict(rec_obj)['metadata'] == {'title': 'Sample title'}


def test_filtered_item_search(client):
    """Test filtered_item_search method."""
    key = 'dc.title'
    string = 'test'
    query_type = 'contains'
    item_links = client.filtered_item_search(key, string, query_type,
                                             selected_collections='')
    assert '1234' in item_links


def test_get_id_from_handle(client):
    """Test get_id_from_handle method."""
    id = client.get_id_from_handle('111.1111')
    assert id == '123'


def test_post_coll_to_comm(client):
    """Test post_coll_to_comm method."""
    comm_handle = '1234'
    coll_name = 'Test Collection'
    coll_id = client.post_coll_to_comm(comm_handle, coll_name)
    assert coll_id == '5678'


def test_post_items_to_coll(client, sample_files_dir):
    """Test post_items_to_coll method."""
    coll_metadata = [{"metadata": [
                     {"key": "file_identifier",
                      "value": "test"},
                     {"key": "dc.title", "value":
                      "Monitoring Works: Getting Teachers",
                      "language": "en_US"},
                     {"key": "dc.relation.isversionof",
                      "value": "repo/0/ao/123"}]}]
    coll_id = '789'
    ingest_type = 'local'
    file_dict = {'test_01': f'{sample_files_dir}/test_01.pdf'}
    item_ids = client.post_items_to_coll(coll_id, coll_metadata, file_dict,
                                         ingest_type)
    for item_id in item_ids:
        assert 'a1b2' == item_id


def test_post_bitstreams_to_item(client, sample_files_dir):
    """Test post_bitstreams_to_item method."""
    item_id = 'a1b2'
    ingest_type = 'local'
    file_identifier = '123'
    file_dict = {'test_02': f'{sample_files_dir}/test_02.pdf',
                 'test_01': f'{sample_files_dir}/test_01.pdf'}
    bit_ids = client.post_bitstreams_to_item(item_id, file_identifier,
                                             file_dict, ingest_type)
    bit_ids_output = []
    for bit_id in bit_ids:
        bit_ids_output.append(bit_id)
    assert bit_ids_output[0] == 'c3d4'
    assert bit_ids_output[1] == 'e5f6'


def test_post_bitstream(client, sample_files_dir):
    """Test post_bitstream method."""
    item_id = 'a1b2'
    ingest_type = 'local'
    file_identifier = '123'
    file_dict = {'test_01': f'{sample_files_dir}/test_01.pdf'}
    bitstream = 'test_01'
    bit_id = client.post_bitstream(item_id, file_identifier, file_dict,
                                   ingest_type, bitstream)
    assert 'c3d4' == bit_id


def test__pop_inst(client):
    """Test _pop_inst method."""
    class_type = models.Collection
    rec_obj = {'name': 'Test title', 'type': 'collection', 'items': []}
    rec_obj = client._pop_inst(class_type, rec_obj)
    assert type(rec_obj) == class_type
    assert rec_obj.name == 'Test title'


def test__build_uuid_list(client):
    """Test _build_uuid_list method."""
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


def test_create_csv_from_list(runner):
    """Test create_csv_from_list function."""
    with runner.isolated_filesystem():
        list_name = ['123']
        models.create_csv_from_list(list_name, 'output')
        with open('output.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                assert row['id'] == '123'


def test_metadata_elems_from_row():
    """Test metadata_elems_from_row function."""
    row = {'title': 'Test title'}
    metadata_elem = models.metadata_elems_from_row(row, 'dc.title', 'title',
                                                   'en_US')
    assert metadata_elem[0]['key'] == 'dc.title'
    assert metadata_elem[0]['value'] == 'Test title'
    assert metadata_elem[0]['language'] == 'en_US'
    metadata_elem = models.metadata_elems_from_row(row, 'dc.title', 'title')
    assert metadata_elem[0]['key'] == 'dc.title'
    assert metadata_elem[0]['value'] == 'Test title'
    assert 'language' not in metadata_elem[0]
    row = {'title': ''}
    metadata_elem = models.metadata_elems_from_row(row, 'dc.title', 'title')
    assert metadata_elem == []
    row = {'title': 'Test title 1|Test title 2'}
    metadata_elem = models.metadata_elems_from_row(row, 'dc.title', 'title',
                                                   'en_US', '|')
    assert metadata_elem[0]['key'] == 'dc.title'
    assert metadata_elem[0]['value'] == 'Test title 1'
    assert metadata_elem[0]['language'] == 'en_US'
    assert metadata_elem[1]['key'] == 'dc.title'
    assert metadata_elem[1]['value'] == 'Test title 2'
    assert metadata_elem[1]['language'] == 'en_US'


# def test_create_ingest_report():
#     assert False


def test_create_metadata_rec():
    metadata_rec = []
    row = {'title': 'Test title'}
    mapping_dict = {'dc.title': ['title']}
    metadata_rec = models.create_metadata_rec(mapping_dict, row, metadata_rec)
    assert metadata_rec[0]['key'] == 'dc.title'
    assert metadata_rec[0]['value'] == 'Test title'
