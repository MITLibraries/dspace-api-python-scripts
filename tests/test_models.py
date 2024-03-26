import attr
from moto import mock_aws

from dsaps.dspace import Bitstream, Collection, Item, MetadataEntry


def test_authenticate(dspace_client):
    """Test authenticate method."""
    email = "test@test.mock"
    password = "1234"
    dspace_client.authenticate(email, password)
    assert dspace_client.user_full_name == "User Name"
    assert dspace_client.cookies == {"JSESSIONID": "11111111"}


def test_filtered_item_search(dspace_client):
    """Test filtered_item_search method."""
    item_links = dspace_client.filtered_item_search(
        key="dc.title", string="test", query_type="contains", selected_collections=""
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


def test_post_bitstream(dspace_client, mocked_s3_bucket):
    """Test post_bitstream method."""
    item_uuid = "e5f6"
    bitstream = Bitstream(
        name="aaaa_001_01.pdf", file_path="s3://mocked-bucket/one-to-one/aaaa_001_01.pdf"
    )
    bit_uuid = dspace_client.post_bitstream(item_uuid, bitstream)
    assert bit_uuid == "g7h8"


def test_post_coll_to_comm(dspace_client):
    """Test post_coll_to_comm method."""
    comm_handle = "111.1111"
    coll_name = "Test Collection"
    coll_uuid = dspace_client.post_coll_to_comm(comm_handle, coll_name)
    assert coll_uuid == "c3d4"


@mock_aws
def test_post_item_to_collection(dspace_client, mocked_s3_bucket):
    """Test post_item_to_collection method."""
    item = Item()
    item.bitstreams = [
        Bitstream(name="aaaa_001_01.pdf", file_path="s3://mocked-bucket/aaaa_001_01.pdf")
    ]
    item.metadata = [
        MetadataEntry(key="dc.title", value="Title 1", language="en_US"),
        MetadataEntry(key="dc.contributor.author", value="May Smith", language=None),
    ]
    collection_uuid = "c3d4"
    item_uuid, item_handle = dspace_client.post_item_to_collection(collection_uuid, item)
    assert item_uuid == "e5f6"
    assert item_handle == "222.2222"


def test__populate_class_instance(dspace_client):
    """Test _populate_class_instance method."""
    class_type = Collection
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
    source_metadata_csv, source_config
):
    collection = Collection.create_metadata_for_items_from_csv(
        source_metadata_csv, source_config["mapping"]
    )
    assert len(collection.items) == 5


# @mock_aws
# def test_collection_post_items(
#     mocked_s3_bucket,
#     dspace_client,
#     source_metadata_csv,
#     source_config,
# ):
#     collection = DSpaceCollection(uuid="c3d4")
#     collection.create_metadata_for_items_from_csv(
#         source_metadata_csv, source_config["mapping"]
#     )
#     items = collection.post_items(dspace_client)
#     print(f"item: {next(items)}")
#     for item in items:
#         assert item.handle != "222.2222"
#         assert item.uuid != "e5f6"


def test_item_metadata_from_csv_row(source_metadata_csv, source_config):
    record = next(source_metadata_csv)
    item = Item.metadata_from_csv_row(record, source_config["mapping"])
    assert attr.asdict(item)["metadata"] == [
        {"key": "dc.title", "value": "Title 1", "language": "en_US"},
        {"key": "dc.contributor.author", "value": "May Smith", "language": None},
    ]
