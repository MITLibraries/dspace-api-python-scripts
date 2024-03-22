import csv

from dsaps.helpers import (
    create_csv_from_list,
    create_ingest_report,
    create_metadata_id_list,
    get_files_from_s3,
    load_source_config,
    match_files_to_metadata,
    match_metadata_to_files,
    parse_value_from_text,
    update_metadata_csv,
)
from dsaps.models import Item

REGEX_ID_BETWEEN_UNDERSCORES = "_(.*)_"
REGEX_ID_BEFORE_UNDERSCORES = "(.*?)_"
REGEX_ID_DDC = ".*-(.*?-.[^_\\.]*)"


def test_load_source_config():
    assert load_source_config("tests/fixtures/source_config.json")["settings"] == {
        "bitstream_folders": ["objects"],
        "id_regex": ".*-(.*?-.*)\\..*$",
    }


def test_create_csv_from_list(output_dir):
    """Test create_csv_from_list function."""
    list_name = ["123"]
    create_csv_from_list(list_name, f"{output_dir}output")
    with open(f"{output_dir}output.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["id"] == "123"


def test_parse_identifier_from_file_name_regex():
    assert (
        parse_value_from_text(text="abc123_01.pdf", regex=REGEX_ID_BEFORE_UNDERSCORES)
        == "abc123"
    )


def test_parse_identifier_from_file_name_ddc_regex():
    assert (
        parse_value_from_text(text="aaaa-bbbb-cccc-02-001.pdf", regex=REGEX_ID_DDC)
        == "02-001"
    )
    assert (
        parse_value_from_text(text="aaaa-bbbb-cccc-02-001_001.pdf", regex=REGEX_ID_DDC)
        == "02-001"
    )


def test_get_files_from_s3_one_file_per_file_id(mocked_s3_bucket, s3_client):
    files = get_files_from_s3(
        s3_path="s3://mocked-bucket/one-to-one/",
        s3_client=s3_client,
        id_regex=REGEX_ID_BETWEEN_UNDERSCORES,
    )
    assert files == {
        "001": [
            "one-to-one/aaaa_001_01.pdf",
        ],
        "002": [
            "one-to-one/aaaa_002_01.pdf",
        ],
    }


def test_get_files_from_s3_many_files_per_file_id(mocked_s3_bucket, s3_client):
    files = get_files_from_s3(
        s3_path="s3://mocked-bucket/many-to-one/",
        s3_client=s3_client,
        id_regex=REGEX_ID_BETWEEN_UNDERSCORES,
    )
    assert files == {
        "003": [
            "many-to-one/bbbb_003_01.jpg",
            "many-to-one/bbbb_003_01.pdf",
            "many-to-one/bbbb_003_02.pdf",
        ],
        "004": ["many-to-one/bbbb_004_01.pdf"],
    }


def test_get_files_from_s3_with_bitstream_folders(mocked_s3_bucket, s3_client):
    files = get_files_from_s3(
        s3_path="s3://mocked-bucket",
        s3_client=s3_client,
        bitstream_folders=["objects"],
        id_regex=REGEX_ID_BETWEEN_UNDERSCORES,
    )
    assert files == {"005": ["nested/prefix/objects/include_005_01.pdf"]}


def test_get_files_from_s3_without_bitstream_folders(mocked_s3_bucket, s3_client):
    files = get_files_from_s3(
        s3_path="s3://mocked-bucket",
        s3_client=s3_client,
        id_regex=REGEX_ID_BETWEEN_UNDERSCORES,
    )
    assert files == {
        "001": [
            "one-to-one/aaaa_001_01.pdf",
        ],
        "002": [
            "one-to-one/aaaa_002_01.pdf",
        ],
        "003": [
            "many-to-one/bbbb_003_01.jpg",
            "many-to-one/bbbb_003_01.pdf",
            "many-to-one/bbbb_003_02.pdf",
        ],
        "004": ["many-to-one/bbbb_004_01.pdf"],
        "005": ["nested/prefix/objects/include_005_01.pdf"],
    }


def test_create_ingest_report(runner, output_dir):
    """Test create_ingest_report function."""
    file_name = "ingest_report.csv"
    items = [Item(source_system_identifier="/repo/0/ao/123", handle="111.1111")]
    create_ingest_report(items, f"{output_dir}{file_name}")
    with open(f"{output_dir}{file_name}") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["uri"] == "/repo/0/ao/123"
            assert row["link"] == "https://hdl.handle.net/111.1111"


def test_create_metadata_id_list():
    """Test create_metadata_id_list function."""
    metadata_path = "tests/fixtures/aspace_metadata_delimited.csv"
    metadata_ids = create_metadata_id_list(metadata_path)
    assert "test" in metadata_ids
    assert "tast" in metadata_ids


def test_match_files_to_metadata():
    """Test match_files_to_metadata function."""
    files_dict = {"test": "test_01.pdf"}
    metadata_ids = ["test", "tast"]
    file_matches = match_files_to_metadata(files_dict.keys(), metadata_ids)
    assert len(file_matches) == 1
    assert "test" in file_matches


def test_match_metadata_to_files():
    """Test match_metadata_to_files function."""
    file_list = {"test": "test_01.pdf", "tast": "tast_01.pdf"}
    metadata_ids = ["test"]
    file_matches = match_metadata_to_files(file_list, metadata_ids)
    assert len(file_matches) == 1
    assert "test" in file_matches


def test_update_metadata_csv(output_dir):
    """Test update_metadata_csv function."""
    metadata_matches = ["test"]
    update_metadata_csv(
        "tests/fixtures/aspace_metadata_delimited.csv",
        output_dir,
        metadata_matches,
        {"test": ["/test/test_01.pdf"]},
    )
    with open(f"{output_dir}updated-aspace_metadata_delimited.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["uri"] == "/repo/0/ao/123"
            assert row["title"] == "Test Item"
            assert row["file_identifier"] == "test"
            assert row["bitstreams"] == "['/test/test_01.pdf']"
