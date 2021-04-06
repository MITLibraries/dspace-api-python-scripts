import attr

from dsaps import models


def test_authenticate(client):
    """Test authenticate method."""
    email = 'test@test.mock'
    password = '1234'
    client.authenticate(email, password)
    assert client.user_full_name == 'User Name'
    assert client.cookies == {'JSESSIONID': '11111111'}


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
    assert id == 'a1b2'


def test_get_record(client):
    """Test get_record method."""
    rec_obj = client.get_record('123', 'items')
    assert attr.asdict(rec_obj)['metadata'] == {'title': 'Sample title'}


def test_post_bitstream(client, input_dir):
    """Test post_bitstream method."""
    item_id = 'e5f6'
    bitstream = models.Bitstream(name='test_01.pdf',
                                 file_path=f'{input_dir}test_01.pdf')
    bit_id = client.post_bitstream(item_id, bitstream)
    assert 'g7h8' == bit_id


def test_post_coll_to_comm(client):
    """Test post_coll_to_comm method."""
    comm_handle = '111.1111'
    coll_name = 'Test Collection'
    coll_id = client.post_coll_to_comm(comm_handle, coll_name)
    assert coll_id == 'c3d4'


def test_post_item_to_collection(client, input_dir):
    """Test post_item_to_collection method."""
    item = models.Item()
    item.bitstreams = [
        models.Bitstream(name='test_01.pdf',
                         file_path=f'{input_dir}test_01.pdf')
        ]
    item.metadata = [
        models.MetadataEntry(key='file_identifier', value='test'),
        models.MetadataEntry(key='dc.title',
                             value='Monitoring Works: Getting Teachers',
                             language='en_US'),
        models.MetadataEntry(key='dc.relation.isversionof',
                             value='repo/0/ao/123')
        ]
    coll_id = 'c3d4'
    item_id = client.post_item_to_collection(coll_id, item)
    assert 'e5f6' == item_id


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


def test_collection_from_csv(aspace_delimited_csv, aspace_mapping):
    collection = models.Collection.from_csv(
        aspace_delimited_csv, aspace_mapping
        )
    assert 2 == len(collection.items)


def test_collection_post_items(client, input_dir):
    raise # TODO: add test for this


def test_item_bitstreams_from_directory(input_dir):
    item = models.Item(metadata=[models.MetadataEntry(
        key='file_identifier', value='test', language=None
        )])
    item.bitstreams_from_directory(input_dir)
    assert 3 == len(item.bitstreams)


def test_item_metadata_from_row(aspace_delimited_csv, aspace_mapping):
    row = next(aspace_delimited_csv)
    item = models.Item.metadata_from_row(row, aspace_mapping)
    assert attr.asdict(item)['metadata'] == [
        {'key': 'file_identifier', 'value': 'tast', 'language': None},
        {'key': 'dc.title', 'value': 'Tast Item', 'language': 'en_US'},
        {'key': 'dc.relation.isversionof', 'value': '/repo/0/ao/456',
         'language': None},
        {'key': 'dc.contributor.author', 'value': 'Smith, John',
         'language': None},
        {'key': 'dc.contributor.author', 'value': 'Smith, Jane',
         'language': None}
        ]