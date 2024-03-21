import attr
from moto import mock_aws

from dsaps.dspace import Bitstream, DSpaceCollection, DSpaceItem, MetadataEntry


def test_authenticate(dspace_client):
    """Test authenticate method."""
    email = "test@test.mock"
    password = "1234"
    dspace_client.authenticate(email, password)
    assert dspace_client.user_full_name == "User Name"
    assert dspace_client.cookies == {"JSESSIONID": "11111111"}


def test_filtered_item_search(dspace_client):
    """Test filtered_item_search method."""
    key = "dc.title"
    string = "test"
    query_type = "contains"
    item_links = dspace_client.filtered_item_search(
        key, string, query_type, selected_collections=""
    )
    assert "1234" in item_links


def test_get_uuid_from_handle(dspace_client):
    """Test get_uuid_from_handle method."""
    id = dspace_client.get_uuid_from_handle("111.1111")
    assert id == "a1b2"


def test_get_record(dspace_client):
    """Test get_record method."""
    rec_obj = dspace_client.get_record("123", "items")
    assert attr.asdict(rec_obj)["metadata"] == {"title": "Sample title"}


def test_post_bitstream(dspace_client, mocked_s3):
    """Test post_bitstream method."""
    item_uuid = "e5f6"
    bitstream = Bitstream(name="test_01.pdf", file_path="s3://test-bucket/test_01.pdf")
    bit_uuid = dspace_client.post_bitstream(item_uuid, bitstream)
    assert bit_uuid == "g7h8"


def test_post_coll_to_comm(dspace_client):
    """Test post_coll_to_comm method."""
    comm_handle = "111.1111"
    coll_name = "Test Collection"
    coll_uuid = dspace_client.post_coll_to_comm(comm_handle, coll_name)
    assert coll_uuid == "c3d4"


@mock_aws
def test_post_item_to_collection(dspace_client, mocked_s3):
    """Test post_item_to_collection method."""
    item = DSpaceItem()
    item.bitstreams = [
        Bitstream(name="test_01.pdf", file_path="s3://test-bucket/test_01.pdf")
    ]
    item.metadata = [
        MetadataEntry(key="file_identifier", value="test"),
        MetadataEntry(
            key="dc.title", value="Monitoring Works: Getting Teachers", language="en_US"
        ),
        MetadataEntry(key="dc.relation.isversionof", value="repo/0/ao/123"),
    ]
    coll_uuid = "c3d4"
    item_uuid, item_handle = dspace_client.post_item_to_collection(coll_uuid, item)
    assert item_uuid == "e5f6"
    assert item_handle == "222.2222"


def test__populate_class_instance(dspace_client):
    """Test _populate_class_instance method."""
    class_type = DSpaceCollection
    rec_obj = {"name": "Test title", "type": "collection", "items": []}
    rec_obj = dspace_client._populate_class_instance(class_type, rec_obj)
    assert type(rec_obj) is class_type
    assert rec_obj.name == "Test title"


def test__build_uuid_list(dspace_client):
    """Test _build_uuid_list method."""
    rec_obj = {"items": [{"uuid": "1234"}]}
    children = "items"
    child_list = dspace_client._build_uuid_list(rec_obj, children)
    assert "1234" in child_list


def test_collection_create_metadata_for_items_from_csv(
    aspace_delimited_csv, aspace_mapping
):
    collection = DSpaceCollection.create_metadata_for_items_from_csv(
        aspace_delimited_csv, aspace_mapping
    )
    assert 2 == len(collection.items)


@mock_aws
def test_collection_post_items(
    mocked_s3,
    dspace_client,
    aspace_delimited_csv,
    aspace_mapping,
):
    collection = DSpaceCollection.create_metadata_for_items_from_csv(
        aspace_delimited_csv, aspace_mapping
    )
    collection.uuid = "c3d4"
    items = collection.post_items(dspace_client)
    for item in items:
        assert item.handle == "222.2222"
        assert item.uuid == "e5f6"


def test_item_metadata_from_csv_row(aspace_delimited_csv, aspace_mapping):
    row = next(aspace_delimited_csv)
    item = DSpaceItem.metadata_from_csv_row(row, aspace_mapping)
    assert attr.asdict(item)["metadata"] == [
        {"key": "dc.title", "value": "Tast Item", "language": "en_US"},
        {"key": "dc.contributor.author", "value": "Smith, John", "language": None},
        {"key": "dc.contributor.author", "value": "Smith, Jane", "language": None},
        {
            "key": "dc.description",
            "value": "More info at /repo/0/ao/456",
            "language": "en_US",
        },
        {"key": "dc.rights", "value": "Totally Free", "language": "en_US"},
        {"key": "dc.rights.uri", "value": "http://free.gov", "language": None},
    ]
