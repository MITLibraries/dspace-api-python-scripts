import attr
import pytest

from dsaps import models


def test_authenticate(client):
    email = "test@test.mock"
    password = "1234"
    client.authenticate(email, password)
    assert client.user_full_name == "User Name"
    assert client.cookies == {"JSESSIONID": "11111111"}


def test_filtered_item_search(client):
    key = "dc.title"
    string = "test"
    query_type = "contains"
    item_links = client.filtered_item_search(
        key, string, query_type, selected_collections=""
    )
    assert "1234" in item_links


def test_get_uuid_from_handle(client):
    id = client.get_uuid_from_handle("111.1111")
    assert id == "a1b2"


def test_get_record_collection(client):
    rec_obj = client.get_record("c3d4", "collections")
    assert attr.asdict(rec_obj) == {
        "handle": None,
        "items": [],
        "link": None,
        "name": "Collection title",
        "objtype": "collection",
        "uuid": "c3d4",
    }


def test_get_record_community(client):
    rec_obj = client.get_record("a1b2", "communities")
    assert attr.asdict(rec_obj) == {
        "handle": None,
        "collections": [],
        "link": None,
        "name": "Community title",
        "objtype": "community",
        "uuid": "a1b2",
    }


def test_get_record_invalid(client):
    with pytest.raises(SystemExit):
        client.get_record("dc", "registries/schema")


def test_get_record_item(client):
    rec_obj = client.get_record("123", "items")
    assert attr.asdict(rec_obj)["metadata"] == {"title": "Sample title"}


def test__build_uuid_list(client):
    rec_obj = {"items": [{"uuid": "1234"}]}
    children = "items"
    child_list = client._build_uuid_list(rec_obj, children)
    assert "1234" in child_list


def test__populate_class_instance(client):
    class_type = models.Collection
    rec_obj = {"name": "Test title", "type": "collection", "items": []}
    rec_obj = client._populate_class_instance(class_type, rec_obj)
    assert type(rec_obj) == class_type
    assert rec_obj.name == "Test title"


def test_collection_post_to_community(client):
    collection = models.Collection()
    community_handle = "111.1111"
    coll_name = "Test Collection"
    coll_uuid = collection.post_to_community(client, community_handle, coll_name)
    assert coll_uuid == "c3d4"


def test_item_post_to_collection(client, input_dir):
    item = models.Item()
    item.bitstreams = [
        models.Bitstream(name="test_01.pdf", file_path=f"{input_dir}test_01.pdf")
    ]
    item.metadata = [
        models.MetadataEntry(key="file_identifier", value="test"),
        models.MetadataEntry(
            key="dc.title", value="Monitoring Works: Getting Teachers", language="en_US"
        ),
        models.MetadataEntry(key="dc.relation.isversionof", value="repo/0/ao/123"),
    ]
    coll_uuid = "c3d4"
    item_uuid, item_handle = item.post_to_collection(client, coll_uuid, item)
    assert item_uuid == "e5f6"
    assert item_handle == "222.2222"


def test_collection_create_metadata_for_items_from_csv(
    aspace_delimited_csv, aspace_mapping
):
    collection = models.Collection.create_metadata_for_items_from_csv(
        aspace_delimited_csv, aspace_mapping
    )
    assert 2 == len(collection.items)


def test_collection_post_items(client, input_dir, aspace_delimited_csv, aspace_mapping):
    collection = models.Collection.create_metadata_for_items_from_csv(
        aspace_delimited_csv, aspace_mapping
    )
    for item in collection.items:
        item.bitstreams_in_directory(input_dir)
    collection.uuid = "c3d4"
    items = collection.post_items(client)
    item = next(items)
    assert item.handle == "222.2222"
    assert item.uuid == "e5f6"
    assert item.bitstreams[0].uuid == "q7r8"


def test_item_delete(client):
    item = models.Item(uuid="m3n4")
    response = item.delete(client)
    assert response == 200


def test_item_bitstreams_in_directory(input_dir):
    item = models.Item(file_identifier="test")
    item.bitstreams_in_directory(input_dir)
    assert 3 == len(item.bitstreams)
    assert item.bitstreams[0].name == "test_01.jpg"
    assert item.bitstreams[1].name == "test_01.pdf"
    assert item.bitstreams[2].name == "test_02.pdf"
    item.bitstreams_in_directory(input_dir, "pdf")
    assert 2 == len(item.bitstreams)
    assert item.bitstreams[0].name == "test_01.pdf"
    assert item.bitstreams[1].name == "test_02.pdf"


def test_item_metadata_from_csv_row_aspace_mapping(
    aspace_delimited_csv, aspace_mapping
):
    row = next(aspace_delimited_csv)
    item = models.Item.metadata_from_csv_row(row, aspace_mapping)
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


def test_item_metadata_from_csv_row_no_file_identifier(
    aspace_delimited_csv, mapping_no_file_identifier
):
    row = next(aspace_delimited_csv)
    item = models.Item.metadata_from_csv_row(row, mapping_no_file_identifier)
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


def test_item_metadata_from_csv_row_no_source_system_identifier(
    aspace_delimited_csv, mapping_no_source_system_identifier
):
    row = next(aspace_delimited_csv)
    item = models.Item.metadata_from_csv_row(row, mapping_no_source_system_identifier)
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


def test_bitstream_delete(client):
    bitstream = models.Bitstream(uuid="o5p6")
    response = bitstream.delete(client)
    assert response == 200


def test_bitstream_post_to_item(client, input_dir):
    item_uuid = "e5f6"
    bitstream = models.Bitstream(
        name="test_01.pdf", file_path=f"{input_dir}test_01.pdf"
    )
    bit_uuid = bitstream.post_bitstream(client, item_uuid, bitstream)
    assert bit_uuid == "g7h8"
